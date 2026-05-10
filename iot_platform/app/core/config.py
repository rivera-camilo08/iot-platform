from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IoT Platform"
    debug: bool = False
    environment: str = "production"

    database_url: str = Field(...)
    jwt_secret_key: str = Field(...)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 15
    jwt_refresh_token_expires_days: int = 30

    mqtt_broker_host: str = Field("mqtt")
    mqtt_broker_port: int = Field(1883)
    mqtt_client_id: str = Field("iot-platform-listener")
    mqtt_topic_template: str = Field("devices/{mac_address}/telemetry")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        case_sensitive=False,
    )


settings = Settings()
