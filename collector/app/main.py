from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api import health, rates
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    app.state.redis = Redis.from_url(settings.collector_redis_url, decode_responses=True)
    async with httpx.AsyncClient(timeout=10) as http:
        app.state.http = http
        yield
    await app.state.redis.aclose()
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title='Collector', lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(rates.router)
    return app


app = create_app()
