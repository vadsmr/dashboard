import datetime as dt
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CryptoPrice
from app.schemas.crypto import CryptoPriceDTO


class CryptoPricesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, prices: Sequence[CryptoPriceDTO]) -> None:
        unique_prices = {(price.coin, price.currency, price.date): price for price in prices}
        if not unique_prices:
            return
        stmt = insert(CryptoPrice).values([price.model_dump() for price in unique_prices.values()])
        stmt = stmt.on_conflict_do_update(
            constraint='uq_crypto_prices_coin_currency_date',
            set_={'price': stmt.excluded.price, 'fetched_at': func.now()},
        )
        await self._session.execute(stmt)

    async def get_by_date(self, date: dt.date) -> list[CryptoPrice]:
        stmt = select(CryptoPrice).where(CryptoPrice.date == date).order_by(CryptoPrice.coin)
        result = await self._session.scalars(stmt)
        return list(result)
