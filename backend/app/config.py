from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./nz_power_plans.db"
    api_title: str = "NZ Power Plans API"
    api_version: str = "1.0.0"
    cors_origins: str = "*"
    debug: bool = True


settings = Settings()
