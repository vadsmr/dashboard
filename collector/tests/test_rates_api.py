from collections.abc import AsyncIterator

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.cbr import CbrClient
from app.db.session import get_session
from app.deps import get_cbr_client
from app.main import create_app
from tests.test_cbr_client import BASE_URL, FIXTURE


def make_api(session: AsyncSession, cbr_status: int) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(cbr_status, content=FIXTURE)

    cbr_http = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_cbr_client] = lambda: CbrClient(cbr_http, BASE_URL)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test')


async def test_collect_then_list(session: AsyncSession) -> None:
    async with make_api(session, 200) as api:
        response = await api.post('/rates/sync')
        assert response.status_code == 200
        assert response.json() == {'saved': 3}

        response = await api.get('/rates', params={'date': '2026-10-18'})

    assert response.status_code == 200
    assert response.json()[0] == {'code': 'EUR', 'date': '2026-10-18', 'rate': '94.103300'}


async def test_cbr_503(session: AsyncSession) -> None:
    async with make_api(session, 503) as api:
        response = await api.post('/rates/sync')
        assert response.status_code == 502


@pytest.mark.parametrize(
    'params',
    [
        {},
        {'date': 'yesterday'},
    ],
    ids=['no date', 'not a date'],
)
async def test_list_rates_with_bad_date(session: AsyncSession, params: dict[str, str]) -> None:
    async with make_api(session, 200) as api:
        response = await api.get('/rates', params=params)

    assert response.status_code == 422


async def test_list_rates_empty(session: AsyncSession) -> None:
    async with make_api(session, 200) as api:
        response = await api.get('/rates', params={'date': '1000-01-01'})
    assert response.status_code == 200
    assert response.json() == []
