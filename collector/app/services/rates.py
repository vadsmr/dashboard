import datetime as dt

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.cbr import CbrClient
from app.db.models import CurrencyRate
from app.repositories.currency_rates import CurrencyRateRepository


class SourceUnavailableError(Exception):
    pass


class RatesService:
    def __init__(self, session: AsyncSession, client: CbrClient) -> None:
        self.session = session
        self.client = client
        self.repository = CurrencyRateRepository(self.session)

    async def collect(self, date: dt.date | None = None) -> int:
        try:
            rates = await self.client.fetch_daily(date)
        except httpx.HTTPError as exc:
            raise SourceUnavailableError(exc) from exc
        await self.repository.upsert_many(rates)
        await self.session.commit()
        return len(rates)

    async def get_rates(self, date: dt.date) -> list[CurrencyRate]:
        return await self.repository.get_by_date(date)
