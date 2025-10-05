from pydantic_settings import BaseSettings, SettingsConfigDict

from app.definitions import ENV_FILE


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DATABASE_URL: str = "url"
    API_KEY: str = "key"
    ECHO: bool = False

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding='utf-8', extra='allow')

settings = Settings()
