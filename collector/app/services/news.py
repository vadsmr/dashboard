import logging
from collections.abc import Mapping

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.rss import RssClient
from app.repositories.news_items import NewsRepository
from app.schemas.news import NewsItemDTO

logger = logging.getLogger(__name__)


class NewsService:
    def __init__(self, session: AsyncSession, client: RssClient, feeds: Mapping[str, str]) -> None:
        self.session = session
        self.client = client
        self.feeds = feeds
        self.repository = NewsRepository(session)

    async def collect(self) -> int:
        added = 0
        for feed, url in self.feeds.items():
            try:
                items = await self.client.fetch_feed(feed, url)
            except httpx.HTTPError:
                logger.warning('Feed %s is unavailable', feed)
                continue
            added += await self.repository.add_new(items)
        await self.session.commit()
        return added

    async def get_latest(self, limit: int) -> list[NewsItemDTO]:
        rows = await self.repository.get_latest(limit)
        return [NewsItemDTO.model_validate(row) for row in rows]
