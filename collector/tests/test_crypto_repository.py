import datetime as dt
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.crypto_prices import CryptoPricesRepository
from app.schemas.crypto import CryptoPriceDTO

DAY = dt.date(2026, 11, 2)


def price(value: str, day: dt.date = DAY) -> CryptoPriceDTO:
    return CryptoPriceDTO(coin='bitcoin', currency='usd', date=day, price=Decimal(value))


async def test_upsert_updates_price_of_the_day(session: AsyncSession) -> None:
    repo = CryptoPricesRepository(session)

    await repo.upsert_many([price('77000')])
    await repo.upsert_many([price('77874.5')])

    rows = await repo.get_by_date(DAY)
    assert [row.price for row in rows] == [Decimal('77874.5')]


async def test_get_by_date_skips_other_days(session: AsyncSession) -> None:
    repo = CryptoPricesRepository(session)
    await repo.upsert_many([price('77000', DAY - dt.timedelta(days=1))])

    assert await repo.get_by_date(DAY) == []
