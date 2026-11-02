from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx

from app.clients.retry import retry_http
from app.schemas.news import NewsItemDTO


class RssClient:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self.http = http

    @retry_http
    async def fetch_feed(self, feed: str, url: str) -> list[NewsItemDTO]:
        response = await self.http.get(url)
        response.raise_for_status()
        return parse_feed(response.content, feed)


def parse_feed(content: bytes, feed: str) -> list[NewsItemDTO]:
    root = ElementTree.fromstring(content)
    result = []
    for item in root.iter('item'):
        title = item.findtext('title', '').strip()
        url = item.findtext('link', '').strip()
        pub_date = item.findtext('pubDate')
        # Неполные элементы пропускаем, а не роняем всю ленту
        if not title or not url or not pub_date:
            continue
        result.append(
            NewsItemDTO(
                feed=feed,
                title=title,
                url=url,
                published_at=parsedate_to_datetime(pub_date),
            )
        )
    return result
