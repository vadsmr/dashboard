import datetime as dt
import json
from collections.abc import Sequence
from decimal import Decimal

import httpx

from app.clients.retry import retry_http
from app.schemas.crypto import CryptoPriceDTO


class CoinGeckoClient:
    def __init__(self, http: httpx.AsyncClient, base_url: str) -> None:
        self.base_url = base_url
        self.http = http

    @retry_http
    async def fetch_prices(
        self, coins: Sequence[str], prices: Sequence[str]
    ) -> list[CryptoPriceDTO]:
        response = await self.http.get(
            f'{self.base_url}/api/v3/simple/price',
            params={
                'ids': ','.join(coins),
                'vs_currencies': ','.join(prices),
            },
        )
        response.raise_for_status()
        return parse_prices(response.content, dt.date.today())


def parse_prices(content: bytes, date: dt.date) -> list[CryptoPriceDTO]:
    data = json.loads(content, parse_float=Decimal)
    result = []
    for coin, prices in data.items():
        for currency, price in prices.items():
            result.append(
                CryptoPriceDTO(
                    coin=coin,
                    currency=currency,
                    date=date,
                    price=price,
                )
            )
    return result
