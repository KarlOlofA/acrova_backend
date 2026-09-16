from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Acrova Quiz API"
    api_prefix: str = "/api"

    # Dev-only placeholder; override via .env / DigitalOcean Managed
    # Postgres connection string in production.
    database_url: str = "postgresql+psycopg://acrova:acrova@localhost:5432/acrova"

    # LinkedIn OAuth (OpenID Connect "Sign in with LinkedIn").
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    linkedin_redirect_uri: Optional[str] = None

    # JWT bearer tokens issued after a successful LinkedIn login.
    # jwt_secret MUST be overridden via env/secret in any real deployment.
    jwt_secret: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    oauth_state_expire_minutes: int = 10

    # Supabase Storage, used to issue signed CV upload URLs.
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_cv_bucket: str = "cvs"

    class Config:
        env_file = ".env"


settings = Settings()
