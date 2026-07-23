from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./nz_power_plans.db"
    api_title: str = "NZ Power Plans API"
    api_version: str = "1.0.0"
    cors_origins: str = "*"
    debug: bool = True

    nz_plan_id: int = 1
    nz_import_sensor: str = "sensor.energy_import_hourly"
    nz_export_sensor: str = "sensor.energy_export_hourly"
    ha_url: str = ""
    ha_token: str = ""


settings = Settings()
