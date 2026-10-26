from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class Source(Protocol):
    name: str

    async def collect(self, session: AsyncSession) -> int: ...
