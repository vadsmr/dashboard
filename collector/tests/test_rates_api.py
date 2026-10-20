from collections.abc import AsyncIterator

import httpx
import pytest
from redis.asyncio import Redis
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.cbr import CbrClient
from app.db.models import CurrencyRate
from app.db.session import get_session
from app.deps import get_cbr_client, get_redis
from app.main import create_app
from tests.test_cbr_client import BASE_URL, FIXTURE


def make_api(session: AsyncSession, cbr_status: int, redis: Redis) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(cbr_status, content=FIXTURE)

    cbr_http = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_cbr_client] = lambda: CbrClient(cbr_http, BASE_URL)
    app.dependency_overrides[get_redis] = lambda: redis
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test')


async def test_collect_then_list(session: AsyncSession, redis: Redis) -> None:
    async with make_api(session, 200, redis) as api:
        response = await api.post('/rates/sync')
        assert response.status_code == 200
        assert response.json() == {'saved': 3}

        response = await api.get('/rates', params={'date': '2026-10-18'})

    assert response.status_code == 200
    assert response.json()[0] == {'code': 'EUR', 'date': '2026-10-18', 'rate': '94.103300'}


async def test_cbr_503(session: AsyncSession, redis: Redis) -> None:
    async with make_api(session, 503, redis) as api:
        response = await api.post('/rates/sync')
        assert response.status_code == 502
        assert response.json() == {'detail': 'CBR is unavailable'}


@pytest.mark.parametrize(
    'params',
    [
        {},
        {'date': 'yesterday'},
    ],
    ids=['no date', 'not a date'],
)
async def test_list_rates_with_bad_date(
    session: AsyncSession, redis: Redis, params: dict[str, str]
) -> None:
    async with make_api(session, 200, redis) as api:
        response = await api.get('/rates', params=params)

    assert response.status_code == 422


async def test_list_rates_empty(session: AsyncSession, redis: Redis) -> None:
    async with make_api(session, 200, redis) as api:
        response = await api.get('/rates', params={'date': '1000-01-01'})
    assert response.status_code == 200
    assert response.json() == []


async def test_cache_clear(session: AsyncSession, redis: Redis) -> None:
    async with make_api(session, 200, redis) as api:
        await api.get('/rates', params={'date': '2026-10-18'})
        await api.post('/rates/sync')
        response = await api.get('/rates', params={'date': '2026-10-18'})

    assert response.status_code == 200
    assert len(response.json()) == 3


async def test_second_read_comes_from_cache(session: AsyncSession, redis: Redis) -> None:
    async with make_api(session, 200, redis) as api:
        await api.post('/rates/sync')
        first = await api.get('/rates', params={'date': '2026-10-18'})
        await session.execute(delete(CurrencyRate))
        second = await api.get('/rates', params={'date': '2026-10-18'})

    assert len(first.json()) == 3
    assert second.json() == first.json()
