import datetime as dt
from collections.abc import Sequence

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.crypto import CoinGeckoClient
from app.repositories.crypto_prices import CryptoPricesRepository
from app.schemas.crypto import CryptoPriceDTO
from app.services.errors import SourceUnavailableError


class CryptoService:
    def __init__(
        self,
        session: AsyncSession,
        client: CoinGeckoClient,
        coins: Sequence[str],
        prices: Sequence[str],
    ) -> None:
        self.session = session
        self.client = client
        self.coins = coins
        self.prices = prices
        self.repository = CryptoPricesRepository(self.session)

    async def collect(self) -> int:
        try:
            rows = await self.client.fetch_prices(self.coins, self.prices)
        except httpx.HTTPError as exc:
            raise SourceUnavailableError('CoinGecko is unavailable') from exc
        await self.repository.upsert_many(rows)
        await self.session.commit()
        return len(rows)

    async def get_prices(self, date: dt.date) -> list[CryptoPriceDTO]:
        rows = await self.repository.get_by_date(date)
        prices = [CryptoPriceDTO.model_validate(row) for row in rows]
        return prices
