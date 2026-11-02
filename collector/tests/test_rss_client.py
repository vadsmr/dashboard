import datetime as dt
from pathlib import Path

import httpx

from app.clients.rss import RssClient, parse_feed

FIXTURE = (Path(__file__).parent / 'fixtures' / 'habr_rss.xml').read_bytes()
FEED_URL = 'https://habr.test/rss/'


def test_parse_feed() -> None:
    items = parse_feed(FIXTURE, 'habr')

    first = items[0]
    assert first.feed == 'habr'
    assert first.title == 'Как мы ускорили PostgreSQL'
    assert first.url == 'https://habr.com/ru/articles/900001/'
    assert first.published_at == dt.datetime(2026, 10, 26, 9, 15, tzinfo=dt.UTC)


def test_parse_feed_keeps_timezone() -> None:
    items = parse_feed(FIXTURE, 'habr')

    # 12:30 по Москве — это 09:30 UTC
    assert items[1].published_at == dt.datetime(2026, 10, 26, 9, 30, tzinfo=dt.UTC)


def test_parse_feed_prefers_guid_over_link() -> None:
    items = parse_feed(FIXTURE, 'habr')

    # У первой статьи guid без utm-меток, у второй guid не ссылка, берём link
    assert [item.url for item in items] == [
        'https://habr.com/ru/articles/900001/',
        'https://habr.com/ru/articles/900002/',
    ]


def test_parse_feed_skips_item_without_link() -> None:
    items = parse_feed(FIXTURE, 'habr')

    assert [item.title for item in items] == ['Как мы ускорили PostgreSQL', 'Asyncio без боли']


async def test_fetch_feed_requests_feed_url() -> None:
    requested = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        items = await RssClient(http).fetch_feed('habr', FEED_URL)

    assert requested == [FEED_URL]
    assert len(items) == 2
