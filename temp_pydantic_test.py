from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(..., env='DATABASE_URL')
    jwt_secret_key: str = Field(..., env='JWT_SECRET_KEY')
    model_config = SettingsConfigDict(env_file=Path('c:/Users/juanc/OneDrive/Escritorio/IoT/.env'))

print(Settings())
