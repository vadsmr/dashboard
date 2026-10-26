import datetime as dt

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.open_meteo import OpenMeteoClient
from app.repositories.weather_daily import WeatherDailyRepository
from app.schemas.weather import Location, WeatherDTO
from app.services.errors import SourceUnavailableError


class WeatherService:
    def __init__(self, session: AsyncSession, client: OpenMeteoClient, location: Location) -> None:
        self.session = session
        self.client = client
        self.location = location
        self.repository = WeatherDailyRepository(self.session)

    async def collect(self) -> int:
        try:
            rows = await self.client.fetch_daily(self.location)
        except httpx.HTTPError as exc:
            raise SourceUnavailableError('Open-Meteo is unavailable') from exc
        await self.repository.upsert_many(rows)
        await self.session.commit()
        return len(rows)

    async def get_forecast(self, date_from: dt.date) -> list[WeatherDTO]:
        rows = await self.repository.get_from(self.location.city, date_from)
        forecast = [WeatherDTO.model_validate(row) for row in rows]
        return forecast
