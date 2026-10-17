import datetime as dt
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.currency_rates import CurrencyRateRepository
from app.schemas.rates import CurrencyRateDTO

DAY = dt.date(2026, 10, 17)


def rate(code: str, value: str) -> CurrencyRateDTO:
    return CurrencyRateDTO(code=code, date=DAY, rate=Decimal(value))


async def test_upsert_inserts_new(session: AsyncSession) -> None:
    repo = CurrencyRateRepository(session)
    await repo.upsert_many([rate('USD', '81.5'), rate('EUR', '94.1')])

    rows = await repo.get_by_date(DAY)

    assert [(r.code, r.rate) for r in rows] == [
        ('EUR', Decimal('94.1')),
        ('USD', Decimal('81.5')),
    ]


async def test_upsert_rate_two_times(session: AsyncSession) -> None:
    repo = CurrencyRateRepository(session)
    await repo.upsert_many([rate('USD', '81.5')])
    await repo.upsert_many([rate('USD', '82.5')])

    rows = await repo.get_by_date(DAY)

    assert [(r.code, r.rate) for r in rows] == [
        ('USD', Decimal('82.5')),
    ]


async def test_upsert_duplicated_rates(session: AsyncSession) -> None:
    repo = CurrencyRateRepository(session)
    await repo.upsert_many([rate('USD', '81.5'), rate('USD', '82.5')])

    rows = await repo.get_by_date(DAY)

    assert [(r.code, r.rate) for r in rows] == [
        ('USD', Decimal('82.5')),
    ]


async def test_upsert_empty_rates(session: AsyncSession) -> None:
    repo = CurrencyRateRepository(session)
    await repo.upsert_many([])

    rows = await repo.get_by_date(DAY)

    assert [(r.code, r.rate) for r in rows] == []


async def test_upsert_and_commit(session: AsyncSession) -> None:
    repo = CurrencyRateRepository(session)
    await repo.upsert_many([rate('USD', '81.5'), rate('EUR', '94.1')])

    await session.commit()
