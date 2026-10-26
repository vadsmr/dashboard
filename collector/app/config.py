import functools
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.weather import Location

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR.parent / '.env', extra='ignore')

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5432
    collector_db: str
    cbr_base_url: str = 'https://www.cbr.ru'
    collect_interval_seconds: int = 3600
    collector_redis_url: str = 'redis://localhost:6379/1'
    cache_ttl_seconds: int = 3600

    open_meteo_base_url: str = 'https://api.open-meteo.com'
    weather_city: str = 'Moscow'
    weather_latitude: float = 55.7558
    weather_longitude: float = 37.6173

    @property
    def database_url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}'
            f'@{self.postgres_host}:{self.postgres_port}/{self.collector_db}'
        )

    @property
    def weather_location(self) -> Location:
        return Location(
            city=self.weather_city,
            latitude=self.weather_latitude,
            longitude=self.weather_longitude,
        )


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()
