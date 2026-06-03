import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IoT Platform"
    debug: bool = False
    environment: str = "production"

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    jwt_secret_key: str = Field(...)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 15
    jwt_refresh_token_expires_days: int = 30

    mqtt_broker_host: str = Field("mqtt")
    mqtt_broker_port: int = Field(1883)
    mqtt_client_id: str = Field("iot-platform-listener")
    mqtt_username: str | None = Field(None)
    mqtt_password: str | None = Field(None)
    mqtt_topic_template: str = Field("devices/{mac_address}/telemetry")
    cors_origins: list[str] = Field(default=["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
