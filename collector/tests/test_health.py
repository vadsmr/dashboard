from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_session
from app.main import create_app


def test_health_ok() -> None:
    with TestClient(create_app()) as client:
        response = client.get('/health')

        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}


def test_health_db_down() -> None:
    async def broken_session() -> AsyncIterator[AsyncMock]:
        session = AsyncMock()
        session.execute.side_effect = OperationalError('SELECT 1', {}, Exception('db down'))
        yield session

    app = create_app()
    app.dependency_overrides[get_session] = broken_session
    with TestClient(app) as client:
        response = client.get('/health')

        assert response.status_code == 503
        assert response.json() == {'status': 'error'}
