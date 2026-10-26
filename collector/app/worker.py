import asyncio
import contextlib
import logging
import signal
from collections.abc import Sequence

import httpx
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.cache.rates import RatesCache
from app.clients.cbr import CbrClient
from app.config import get_settings
from app.sources.base import Source
from app.sources.cbr import CbrSource

logger = logging.getLogger('app.worker')


async def collect_all(
    sessionmaker: async_sessionmaker[AsyncSession], sources: Sequence[Source]
) -> None:
    for source in sources:
        try:
            async with sessionmaker() as session:
                saved = await source.collect(session)
        except Exception:
            logger.exception('%s: collection failed', source.name)
        else:
            logger.info('%s: saved %s', source.name, saved)


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    redis = Redis.from_url(settings.collector_redis_url, decode_responses=True)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, stop.set)
    loop.add_signal_handler(signal.SIGINT, stop.set)

    async with httpx.AsyncClient(timeout=10) as http:
        sources: list[Source] = [
            CbrSource(
                CbrClient(http, settings.cbr_base_url),
                RatesCache(redis, settings.cache_ttl_seconds),
            ),
        ]
        while not stop.is_set():
            await collect_all(sessionmaker, sources)
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=settings.collect_interval_seconds)

    await redis.aclose()
    await engine.dispose()
    logger.info('Worker stopped')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    asyncio.run(main())
