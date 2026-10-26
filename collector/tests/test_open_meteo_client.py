import datetime as dt
from decimal import Decimal
from pathlib import Path

import httpx

from app.clients.open_meteo import OpenMeteoClient
from app.schemas.weather import Location

FIXTURE = (Path(__file__).parent / 'fixtures' / 'open_meteo_daily.json').read_bytes()
BASE_URL = 'https://api.open-meteo.test'
MOSCOW = Location(city='Moscow', latitude=55.75, longitude=37.62)


async def test_fetch_daily_parses_weather() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        rows = await OpenMeteoClient(http, BASE_URL).fetch_daily(MOSCOW)

    assert [(r.temp_max, r.temp_min) for r in rows] == [
        (Decimal('11.0'), Decimal('-0.8')),
        (Decimal('10.1'), Decimal('3.0')),
        (Decimal('10.4'), Decimal('4.1')),
    ]
    assert rows[0].city == 'Moscow'
    assert rows[0].date == dt.date(2026, 10, 26)
    assert rows[0].precipitation == Decimal('2.3')


async def test_fetch_daily_sends_coordinates() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        await OpenMeteoClient(http, BASE_URL).fetch_daily(MOSCOW)

    params = requests[0].url.params
    assert requests[0].url.path == '/v1/forecast'
    assert params['latitude'] == '55.75'
    assert params['longitude'] == '37.62'
