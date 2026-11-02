import datetime as dt
from collections.abc import AsyncIterator

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.crypto import CoinGeckoClient
from app.db.session import get_session
from app.deps import get_coin_gecko_client
from app.main import create_app
from tests.test_coingecko_client import BASE_URL, FIXTURE


def make_api(session: AsyncSession, coingecko_status: int) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(coingecko_status, content=FIXTURE)

    coingecko_http = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_coin_gecko_client] = lambda: CoinGeckoClient(
        coingecko_http, BASE_URL
    )
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test')


async def test_sync_then_list(session: AsyncSession) -> None:
    today = dt.date.today().isoformat()

    async with make_api(session, 200) as api:
        response = await api.post('/crypto/sync')
        assert response.status_code == 200
        assert response.json() == {'saved': 4}

        response = await api.get('/crypto_prices', params={'date': today})

    assert response.status_code == 200
    assert len(response.json()) == 4
    assert response.json()[0]['coin'] == 'bitcoin'


async def test_coingecko_down(session: AsyncSession) -> None:
    async with make_api(session, 503) as api:
        response = await api.post('/crypto/sync')

    assert response.status_code == 502
    assert response.json() == {'detail': 'CoinGecko is unavailable'}
