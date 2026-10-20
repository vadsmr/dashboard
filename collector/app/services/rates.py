import datetime as dt

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.rates import RatesCache
from app.clients.cbr import CbrClient
from app.repositories.currency_rates import CurrencyRateRepository
from app.schemas.rates import CurrencyRateDTO


class SourceUnavailableError(Exception):
    pass


class RatesService:
    def __init__(self, session: AsyncSession, client: CbrClient, cache: RatesCache) -> None:
        self.session = session
        self.client = client
        self.cache = cache
        self.repository = CurrencyRateRepository(self.session)

    async def collect(self, date: dt.date | None = None) -> int:
        try:
            rates = await self.client.fetch_daily(date)
        except httpx.HTTPError as exc:
            raise SourceUnavailableError('CBR is unavailable') from exc
        await self.repository.upsert_many(rates)
        await self.session.commit()
        for rate_date in {rate.date for rate in rates}:
            await self.cache.invalidate(rate_date)
        return len(rates)

    async def get_rates(self, date: dt.date) -> list[CurrencyRateDTO]:
        cached = await self.cache.get(date)
        if cached is not None:
            return cached
        rows = await self.repository.get_by_date(date)
        rates = [CurrencyRateDTO.model_validate(row) for row in rows]
        await self.cache.set(date, rates)
        return rates
