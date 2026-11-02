import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.news_items import NewsRepository
from app.schemas.news import NewsItemDTO

NOON = dt.datetime(2026, 10, 26, 12, 0, tzinfo=dt.UTC)


def news(url: str, title: str = 'Title', hours: int = 0) -> NewsItemDTO:
    return NewsItemDTO(
        feed='habr', title=title, url=url, published_at=NOON + dt.timedelta(hours=hours)
    )


async def test_add_new_counts_only_new(session: AsyncSession) -> None:
    repo = NewsRepository(session)

    assert await repo.add_new([news('https://a'), news('https://b')]) == 2
    assert await repo.add_new([news('https://b'), news('https://c')]) == 1


async def test_add_new_keeps_first_title(session: AsyncSession) -> None:
    repo = NewsRepository(session)

    await repo.add_new([news('https://a', title='First')])
    await repo.add_new([news('https://a', title='Second')])

    rows = await repo.get_latest(10)
    assert [row.title for row in rows] == ['First']


async def test_get_latest_newest_first(session: AsyncSession) -> None:
    repo = NewsRepository(session)
    await repo.add_new([news('https://old', hours=0), news('https://new', hours=2)])

    rows = await repo.get_latest(1)

    assert [row.url for row in rows] == ['https://new']
