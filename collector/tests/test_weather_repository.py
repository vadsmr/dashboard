import datetime as dt
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.weather_daily import WeatherDailyRepository
from app.schemas.weather import WeatherDTO

DAY = dt.date(2026, 10, 27)


def forecast(day: dt.date, temp_max: str) -> WeatherDTO:
    return WeatherDTO(
        city='Moscow',
        date=day,
        temp_max=Decimal(temp_max),
        temp_min=Decimal('0.0'),
        precipitation=Decimal('0.0'),
    )


async def test_upsert_replaces_old_forecast(session: AsyncSession) -> None:
    repo = WeatherDailyRepository(session)

    await repo.upsert_many([forecast(DAY, '5.0')])
    await repo.upsert_many([forecast(DAY, '7.5')])

    rows = await repo.get_from('Moscow', DAY)
    assert [row.temp_max for row in rows] == [Decimal('7.5')]


async def test_get_from_includes_start_day_and_sorts(session: AsyncSession) -> None:
    repo = WeatherDailyRepository(session)
    yesterday = DAY - dt.timedelta(days=1)
    tomorrow = DAY + dt.timedelta(days=1)
    await repo.upsert_many(
        [forecast(tomorrow, '3.0'), forecast(yesterday, '1.0'), forecast(DAY, '2.0')]
    )

    rows = await repo.get_from('Moscow', DAY)

    assert [row.date for row in rows] == [DAY, tomorrow]


async def test_get_from_filters_by_city(session: AsyncSession) -> None:
    repo = WeatherDailyRepository(session)
    await repo.upsert_many([forecast(DAY, '5.0')])

    assert await repo.get_from('Kazan', DAY) == []
