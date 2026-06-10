from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: SecretStr
    JWT_ALGITHAM: SecretStr
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore'
    )

Config = Settings()