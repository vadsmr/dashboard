from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.open_meteo import OpenMeteoClient
from app.schemas.weather import Location
from app.services.weather import WeatherService


class WeatherSource:
    name = 'open-meteo'

    def __init__(self, client: OpenMeteoClient, location: Location) -> None:
        self.client = client
        self.location = location

    async def collect(self, session: AsyncSession) -> int:
        return await WeatherService(session, self.client, self.location).collect()
