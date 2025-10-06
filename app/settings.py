from pydantic_settings import BaseSettings, SettingsConfigDict

from app.definitions import ENV_FILE


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    API_KEY: str = "key"
    ECHO: bool = False
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "org_db"
    POSTGRES_HOST: str = "db"

    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}'

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding='utf-8')

settings = Settings()
