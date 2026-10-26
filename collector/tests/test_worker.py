import logging

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.worker import collect_all


class FakeSource:
    def __init__(self, name: str, fail: bool = False) -> None:
        self.name = name
        self.fail = fail
        self.calls = 0

    async def collect(self, session: AsyncSession) -> int:
        self.calls += 1
        if self.fail:
            raise RuntimeError('boom')
        return 5


async def test_failed_source_does_not_stop_others(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    broken = FakeSource('broken', fail=True)
    healthy = FakeSource('healthy')

    await collect_all(async_sessionmaker(), [broken, healthy])

    assert broken.calls == 1
    assert healthy.calls == 1
    assert 'broken: collection failed' in caplog.text
    assert 'healthy: saved 5' in caplog.text
