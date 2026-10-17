import datetime as dt
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CurrencyRate
from app.schemas.rates import CurrencyRateDTO


class CurrencyRateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, rates: Sequence[CurrencyRateDTO]) -> None:
        unique_rates = {(rate.code, rate.date): rate for rate in rates}
        if not unique_rates:
            return
        stmt = insert(CurrencyRate).values([rate.model_dump() for rate in unique_rates.values()])
        stmt = stmt.on_conflict_do_update(
            constraint='uq_currency_rates_code_date',
            set_={'rate': stmt.excluded.rate, 'fetched_at': func.now()},
        )
        await self._session.execute(stmt)

    async def get_by_date(self, date: dt.date) -> list[CurrencyRate]:
        stmt = select(CurrencyRate).where(CurrencyRate.date == date).order_by(CurrencyRate.code)
        result = await self._session.scalars(stmt)
        return list(result)
