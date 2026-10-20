import datetime as dt

from pydantic import TypeAdapter
from redis.asyncio import Redis

from app.schemas.rates import CurrencyRateDTO

RATES_ADAPTER = TypeAdapter(list[CurrencyRateDTO])


class RatesCache:
    def __init__(self, redis: Redis, ttl: int) -> None:
        self.redis = redis
        self.ttl = ttl

    async def get(self, date: dt.date) -> list[CurrencyRateDTO] | None:
        cached_rates = await self.redis.get(self._key(date))
        if cached_rates is None:
            return None
        return RATES_ADAPTER.validate_json(cached_rates)

    async def set(self, date: dt.date, rates: list[CurrencyRateDTO]) -> None:
        await self.redis.set(self._key(date), RATES_ADAPTER.dump_json(rates), ex=self.ttl)

    async def invalidate(self, date: dt.date) -> None:
        await self.redis.delete(self._key(date))

    def _key(self, date: dt.date) -> str:
        return f'rates:{date.isoformat()}'
