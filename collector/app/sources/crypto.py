from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.crypto import CoinGeckoClient
from app.services.crypto import CryptoService


class CryptoSource:
    name = 'coingecko'

    def __init__(
        self, client: CoinGeckoClient, coins: Sequence[str], currencies: Sequence[str]
    ) -> None:
        self.client = client
        self.coins = coins
        self.currencies = currencies

    async def collect(self, session: AsyncSession) -> int:
        return await CryptoService(session, self.client, self.coins, self.currencies).collect()
