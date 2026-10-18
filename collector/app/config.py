import functools
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR.parent / '.env', extra='ignore')

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5432
    collector_db: str
    cbr_base_url: str = 'https://www.cbr.ru'

    @property
    def database_url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}'
            f'@{self.postgres_host}:{self.postgres_port}/{self.collector_db}'
        )


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()
