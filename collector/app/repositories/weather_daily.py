import datetime as dt
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WeatherDaily
from app.schemas.weather import WeatherDTO


class WeatherDailyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, rows: Sequence[WeatherDTO]) -> None:
        unique_rows = {(row.city, row.date): row for row in rows}
        if not unique_rows:
            return
        stmt = insert(WeatherDaily).values([rate.model_dump() for rate in unique_rows.values()])
        stmt = stmt.on_conflict_do_update(
            constraint='uq_weather_daily_city_date',
            set_={
                'temp_max': stmt.excluded.temp_max,
                'temp_min': stmt.excluded.temp_min,
                'precipitation': stmt.excluded.precipitation,
                'fetched_at': func.now(),
            },
        )
        await self._session.execute(stmt)

    async def get_from(self, city: str, date_from: dt.date) -> list[WeatherDaily]:
        stmt = (
            select(WeatherDaily)
            .where(WeatherDaily.city == city, WeatherDaily.date >= date_from)
            .order_by(WeatherDaily.date)
        )
        result = await self._session.scalars(stmt)
        return list(result)
