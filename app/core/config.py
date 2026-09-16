from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Acrova Quiz API"
    api_prefix: str = "/api"

    class Config:
        env_file = ".env"


settings = Settings()
