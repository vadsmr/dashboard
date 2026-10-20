from typing import Annotated

import httpx
from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.rates import RatesCache
from app.clients.cbr import CbrClient
from app.config import get_settings
from app.db.session import get_session
from app.services.rates import RatesService


def get_http(request: Request) -> httpx.AsyncClient:
    http: httpx.AsyncClient = request.app.state.http
    return http


def get_cbr_client(http: Annotated[httpx.AsyncClient, Depends(get_http)]) -> CbrClient:
    return CbrClient(http, get_settings().cbr_base_url)


def get_redis(request: Request) -> Redis:
    redis: Redis = request.app.state.redis
    return redis


def get_rates_cache(redis: Annotated[Redis, Depends(get_redis)]) -> RatesCache:
    return RatesCache(redis, ttl=get_settings().cache_ttl_seconds)


def get_rates_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    client: Annotated[CbrClient, Depends(get_cbr_client)],
    cache: Annotated[RatesCache, Depends(get_rates_cache)],
) -> RatesService:
    return RatesService(session, client, cache)


RatesServiceDep = Annotated[RatesService, Depends(get_rates_service)]
