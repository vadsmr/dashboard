from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NewsItem
from app.schemas.news import NewsItemDTO


class NewsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_new(self, items: Sequence[NewsItemDTO]) -> int:
        """Сохраняет только новые новости и возвращает, сколько добавилось."""
        unique_items = {item.url: item for item in items}
        if not unique_items:
            return 0
        stmt = (
            insert(NewsItem)
            .values([item.model_dump() for item in unique_items.values()])
            .on_conflict_do_nothing(index_elements=['url'])
            .returning(NewsItem.id)
        )
        result = await self._session.scalars(stmt)
        return len(result.all())

    async def get_latest(self, limit: int) -> list[NewsItem]:
        stmt = select(NewsItem).order_by(NewsItem.published_at.desc()).limit(limit)
        result = await self._session.scalars(stmt)
        return list(result)
