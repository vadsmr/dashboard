from collections.abc import Mapping

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.rss import RssClient
from app.services.news import NewsService


class NewsSource:
    name = 'rss'

    def __init__(self, client: RssClient, feeds: Mapping[str, str]) -> None:
        self.client = client
        self.feeds = feeds

    async def collect(self, session: AsyncSession) -> int:
        return await NewsService(session, self.client, self.feeds).collect()
