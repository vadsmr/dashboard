from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from tenacity import wait_none

from app.clients.cbr import CbrClient
from app.config import get_settings


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            join_transaction_mode='create_savepoint',
            expire_on_commit=False,
        )
        yield session
        await session.close()
        await transaction.rollback()
    await engine.dispose()


@pytest.fixture(autouse=True)
def no_retry_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(CbrClient.fetch_daily.retry, 'wait', wait_none())
