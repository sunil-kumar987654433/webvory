from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: SecretStr
    JWT_ALGITHAM: SecretStr
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore'
    )

Config = Settings()