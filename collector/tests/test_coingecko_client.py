import datetime as dt
from decimal import Decimal
from pathlib import Path

import httpx

from app.clients.crypto import CoinGeckoClient, parse_prices

FIXTURE = (Path(__file__).parent / 'fixtures' / 'coingecko_price.json').read_bytes()
BASE_URL = 'https://coingecko.test'
DAY = dt.date(2026, 11, 2)


def test_parse_prices_flattens_coins_and_currencies() -> None:
    prices = parse_prices(FIXTURE, DAY)

    assert [(p.coin, p.currency) for p in prices] == [
        ('bitcoin', 'rub'),
        ('bitcoin', 'usd'),
        ('ethereum', 'rub'),
        ('ethereum', 'usd'),
    ]
    assert {p.date for p in prices} == {DAY}


def test_parse_prices_keeps_precision() -> None:
    prices = parse_prices(FIXTURE, DAY)

    assert prices[3].price == Decimal('2456.78901234567891')


async def test_fetch_prices_sends_coins_and_currencies() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        await CoinGeckoClient(http, BASE_URL).fetch_prices(['bitcoin', 'ethereum'], ['usd', 'rub'])

    params = requests[0].url.params
    assert requests[0].url.path == '/api/v3/simple/price'
    assert params['ids'] == 'bitcoin,ethereum'
    assert params['vs_currencies'] == 'usd,rub'
