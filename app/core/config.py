from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Acrova Quiz API"
    api_prefix: str = "/api"

    # Dev-only placeholder; override via .env / DigitalOcean Managed
    # Postgres connection string in production.
    database_url: str = "postgresql+psycopg://acrova:acrova@localhost:5432/acrova"

    # TODO: LinkedIn OAuth wiring, unset until the flow is implemented.
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    linkedin_redirect_uri: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
