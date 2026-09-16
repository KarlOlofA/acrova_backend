from enum import Enum
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Placeholders that are fine locally but must never reach a deployment.
DEV_JWT_SECRET = "dev-only-insecure-secret-change-me"
DEV_DATABASE_URL = "postgresql+psycopg://acrova:acrova@localhost:5432/acrova"


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
    port: int = 8000

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

    # Dev-only placeholder; override via .env / DigitalOcean Managed
    # Postgres connection string in production.
    database_url: str = DEV_DATABASE_URL

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

    @model_validator(mode="after")
    def _reject_dev_placeholders_in_production(self) -> "Settings":
        if self.is_production:
            unset = [
                name
                for name, value, placeholder in (
                    ("JWT_SECRET", self.jwt_secret, DEV_JWT_SECRET),
                    ("DATABASE_URL", self.database_url, DEV_DATABASE_URL),
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
