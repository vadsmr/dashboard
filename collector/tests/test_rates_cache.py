import datetime as dt
from decimal import Decimal

from redis.asyncio import Redis

from app.cache.rates import RatesCache
from app.schemas.rates import CurrencyRateDTO

DATE = dt.date(2026, 10, 18)
RATES = [CurrencyRateDTO(code='USD', date=DATE, rate=Decimal('81.250000'))]


async def test_miss_returns_none(redis: Redis) -> None:
    assert await RatesCache(redis, ttl=60).get(DATE) is None


async def test_set_then_get(redis: Redis) -> None:
    cache = RatesCache(redis, ttl=60)
    await cache.set(DATE, RATES)

    assert await cache.get(DATE) == RATES
    assert 0 < await redis.ttl('rates:2026-10-18') <= 60


async def test_empty_list_is_cached(redis: Redis) -> None:
    cache = RatesCache(redis, ttl=60)
    await cache.set(DATE, [])

    assert await cache.get(DATE) == []


async def test_invalidate(redis: Redis) -> None:
    cache = RatesCache(redis, ttl=60)
    await cache.set(DATE, RATES)
    await cache.invalidate(DATE)

    assert await cache.get(DATE) is None
