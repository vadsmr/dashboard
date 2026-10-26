from collections.abc import AsyncIterator

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.open_meteo import OpenMeteoClient
from app.db.session import get_session
from app.deps import get_open_meteo_client
from app.main import create_app
from tests.test_open_meteo_client import BASE_URL, FIXTURE


def make_api(session: AsyncSession, meteo_status: int) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(meteo_status, content=FIXTURE)

    meteo_http = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_open_meteo_client] = lambda: OpenMeteoClient(meteo_http, BASE_URL)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test')


async def test_sync_then_forecast(session: AsyncSession) -> None:
    async with make_api(session, 200) as api:
        response = await api.post('/weather/sync')
        assert response.status_code == 200
        assert response.json() == {'saved': 3}

        response = await api.get('/weather', params={'date_from': '2026-10-27'})

    assert response.status_code == 200
    assert [row['date'] for row in response.json()] == ['2026-10-27', '2026-10-28']
    assert response.json()[0]['temp_max'] == '10.1'


async def test_open_meteo_down(session: AsyncSession) -> None:
    async with make_api(session, 503) as api:
        response = await api.post('/weather/sync')

    assert response.status_code == 502
    assert response.json() == {'detail': 'Open-Meteo is unavailable'}
