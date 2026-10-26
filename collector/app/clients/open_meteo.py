from typing import Any

import httpx

from app.clients.retry import retry_http
from app.schemas.weather import Location, WeatherDTO


class OpenMeteoClient:
    def __init__(self, http: httpx.AsyncClient, base_url: str) -> None:
        self.base_url = base_url
        self.http = http

    @retry_http
    async def fetch_daily(self, location: Location) -> list[WeatherDTO]:
        response = await self.http.get(
            f'{self.base_url}/v1/forecast',
            params={
                'latitude': location.latitude,
                'longitude': location.longitude,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'auto',
                'forecast_days': 7,
            },
        )
        response.raise_for_status()
        return parse_daily(response.json(), location.city)


def parse_daily(data: dict[str, Any], city: str) -> list[WeatherDTO]:
    daily = data['daily']
    result = []
    for day, t_max, t_min, precipitation in zip(
        daily['time'],
        daily['temperature_2m_max'],
        daily['temperature_2m_min'],
        daily['precipitation_sum'],
        strict=True,
    ):
        weather = WeatherDTO(
            city=city, date=day, temp_max=t_max, temp_min=t_min, precipitation=precipitation
        )
        result.append(weather)
    return result
