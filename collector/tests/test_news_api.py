from collections.abc import AsyncIterator

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.rss import RssClient
from app.db.session import get_session
from app.deps import get_rss_client
from app.main import create_app
from tests.test_rss_client import FIXTURE


def make_api(session: AsyncSession, rss_status: int) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(rss_status, content=FIXTURE)

    rss_http = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_rss_client] = lambda: RssClient(rss_http)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test')


async def test_sync_then_list(session: AsyncSession) -> None:
    async with make_api(session, 200) as api:
        response = await api.post('/news/sync')
        assert response.json() == {'added': 2}

        response = await api.post('/news/sync')
        assert response.json() == {'added': 0}

        response = await api.get('/news', params={'limit': 1})

    assert response.status_code == 200
    # 12:30 +0300 = 09:30 UTC, это позже 09:15 UTC, поэтому эта статья свежее
    assert [item['title'] for item in response.json()] == ['Asyncio без боли']


async def test_feed_down_is_skipped(session: AsyncSession) -> None:
    async with make_api(session, 404) as api:
        response = await api.post('/news/sync')

    assert response.status_code == 200
    assert response.json() == {'added': 0}


async def test_limit_is_bounded(session: AsyncSession) -> None:
    async with make_api(session, 200) as api:
        response = await api.get('/news', params={'limit': 1000})

    assert response.status_code == 422
