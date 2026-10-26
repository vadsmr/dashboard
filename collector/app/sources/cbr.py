from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.rates import RatesCache
from app.clients.cbr import CbrClient
from app.services.rates import RatesService


class CbrSource:
    name = 'cbr'

    def __init__(self, client: CbrClient, cache: RatesCache) -> None:
        self.client = client
        self.cache = cache

    async def collect(self, session: AsyncSession) -> int:
        return await RatesService(session, self.client, self.cache).collect()
