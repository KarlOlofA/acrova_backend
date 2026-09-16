import re
from enum import Enum
from typing import Any, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# App Platform "bindable variables" (${APP_URL}, ${db.DATABASE_URL}, ...) are
# substituted by DigitalOcean at deploy time. A reference that names no
# existing component, or one resolved too early in the deploy, is handed to the
# process as literal text and then fails deep inside whatever consumes it.
# DATABASE_URL is a plain secret now, so any ${...} left in it is a mistake.
UNRESOLVED_BINDABLE = re.compile(r"\$\{[^}]*\}")

# Placeholder that is fine locally but must never reach a deployment.
DEV_JWT_SECRET = "dev-only-insecure-secret-change-me"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Single switch for the whole app: ENVIRONMENT=development | production.
    # Everything that differs between local dev and DigitalOcean (auto-reload,
    # log level, CORS defaults, required secrets) is derived from this.
    environment: Environment = Environment.DEVELOPMENT

    app_name: str = "Acrova Quiz API"
    api_prefix: str = "/api"

    # --- where the process listens -------------------------------------
    # HOST is the interface uvicorn binds to: 0.0.0.0 to accept traffic from
    # outside the machine (required on DigitalOcean), 127.0.0.1 for local only.
    # PORT is injected by App Platform, so don't hardcode it there.
    host: str = "0.0.0.0"
    port: int = 8080

    # --- where clients reach the API ------------------------------------
    # The public address of this server. On App Platform set it to the app
    # URL; on a Droplet set it to http://<droplet-ip>:<port>. Used to build
    # the OAuth redirect URI and the OpenAPI "servers" block, so LinkedIn and
    # Swagger point at the deployed host instead of localhost.
    public_base_url: Optional[str] = None

    # Comma-separated list of allowed browser origins, or "*" for any.
    cors_origins: str = "*"

    # Overrides for the environment-derived defaults below. Leave unset to
    # let ENVIRONMENT decide.
    reload: Optional[bool] = None
    log_level: Optional[str] = None
    docs_enabled: bool = True

    # Required everywhere, with no default on purpose. A default here is a
    # trap: when the deployed environment loses DATABASE_URL the process
    # silently dials the fallback instead of failing, and the misconfiguration
    # surfaces as a connection-refused traceback from deep inside SQLAlchemy
    # rather than as "DATABASE_URL is not set". Locally, copy .env.example to
    # .env - it ships a working value for the docker Postgres one-liner.
    database_url: str

    # LinkedIn OAuth (OpenID Connect "Sign in with LinkedIn").
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    # Leave unset to derive it from public_base_url / host + port.
    linkedin_redirect_uri: Optional[str] = None

    # JWT bearer tokens issued after a successful LinkedIn login.
    # jwt_secret MUST be overridden via env/secret in any real deployment.
    jwt_secret: str = DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    oauth_state_expire_minutes: int = 10

    # Supabase Storage, used to issue signed CV upload URLs.
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_cv_bucket: str = "cvs"

    @property
    def is_production(self) -> bool:
        return self.environment is Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.environment is Environment.DEVELOPMENT

    @property
    def reload_enabled(self) -> bool:
        """Auto-reload on code changes: handy in dev, never in production."""
        return self.is_development if self.reload is None else self.reload

    @property
    def effective_log_level(self) -> str:
        if self.log_level:
            return self.log_level.lower()
        return "debug" if self.is_development else "info"

    @property
    def base_url(self) -> str:
        """Public URL of this API, without a trailing slash."""
        if self.public_base_url:
            return self.public_base_url.rstrip("/")
        # 0.0.0.0 is a bind address, not something a client can call.
        host = "127.0.0.1" if self.host in ("0.0.0.0", "::") else self.host
        return f"http://{host}:{self.port}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_linkedin_redirect_uri(self) -> str:
        """LINKEDIN_REDIRECT_URI if set, otherwise derived from base_url.

        Must match the redirect URI registered in the LinkedIn app exactly.
        """
        if self.linkedin_redirect_uri:
            return self.linkedin_redirect_uri
        return f"{self.base_url}{self.api_prefix}/auth/linkedin/callback"

    @model_validator(mode="before")
    @classmethod
    def _require_database_url(cls, data: Any) -> Any:
        """Report a DATABASE_URL that was never provided at all.

        Pydantic's own message for a missing required field names the *field*
        ("database_url: Field required"), not the environment variable to set,
        so replace it with something actionable.
        """
        if isinstance(data, dict) and "database_url" not in data:
            raise ValueError(
                "DATABASE_URL is not set. Point it at the Postgres connection "
                "string:\n"
                "  - locally: cp .env.example .env (its default matches the "
                "docker Postgres one-liner in that file)\n"
                "  - DigitalOcean App Platform: a RUN_TIME secret on the api "
                "service, set in the console - a `type: SECRET` entry with no "
                "value in .do/app.yaml does not create the variable, it only "
                "preserves an existing one."
            )
        return data

    @field_validator("database_url", mode="after")
    @classmethod
    def _check_database_url(cls, url: str) -> str:
        """Catch a DATABASE_URL that never got a real value.

        Without this the failure surfaces as SQLAlchemy's opaque "Could not
        parse SQLAlchemy URL from given URL string" at import time.
        """
        url = url.strip().strip("\"'")
        if not url:
            raise ValueError(
                "DATABASE_URL is empty. Set it to the Postgres connection "
                "string - on DigitalOcean App Platform, as a RUN_TIME secret on "
                "the api service (see .do/app.yaml)."
            )
        if UNRESOLVED_BINDABLE.search(url):
            raise ValueError(
                f"DATABASE_URL was passed through unsubstituted as {url!r}. "
                "It should be a literal connection string, not a DigitalOcean "
                "bindable reference - a ${...} naming no app component, or read "
                "at BUILD_TIME, is left as plain text."
            )
        if "://" not in url:
            raise ValueError(
                "DATABASE_URL is not a connection URL (expected something like "
                "postgresql://user:password@host:5432/dbname)."
            )
        return url

    @model_validator(mode="after")
    def _reject_dev_placeholders_in_production(self) -> "Settings":
        if self.is_production:
            unset = [
                name
                for name, value, placeholder in (
                    ("JWT_SECRET", self.jwt_secret, DEV_JWT_SECRET),
                )
                if value == placeholder
            ]
            if unset:
                raise ValueError(
                    "ENVIRONMENT=production but these still hold their local dev "
                    f"placeholder values: {', '.join(unset)}. Set them in the "
                    "environment before starting the server."
                )
        return self


settings = Settings()
