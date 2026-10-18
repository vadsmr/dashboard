import datetime as dt
from decimal import Decimal
from pathlib import Path

import httpx

from app.clients.cbr import CbrClient

FIXTURE = (Path(__file__).parent / 'fixtures' / 'cbr_daily.xml').read_bytes()
BASE_URL = 'https://cbr.test'


async def test_fetch_daily_parses_rates() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        rates = await CbrClient(http, BASE_URL).fetch_daily()

    assert [(r.code, r.rate) for r in rates] == [
        ('USD', Decimal('81.5012')),
        ('EUR', Decimal('94.1033')),
        ('JPY', Decimal('0.54321')),
    ]
    assert {r.date for r in rates} == {dt.date(2026, 10, 18)}


async def test_fetch_daily_date_in_url() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        await CbrClient(http, BASE_URL).fetch_daily(dt.date(2026, 10, 17))

    assert str(requests[0].url) == 'https://cbr.test/scripts/XML_daily.asp?date=17%2F10%2F2026'


async def test_fetch_daily_503() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        try:
            await CbrClient(http, BASE_URL).fetch_daily()
        except httpx.HTTPStatusError as e:
            assert e.response.status_code == 503
