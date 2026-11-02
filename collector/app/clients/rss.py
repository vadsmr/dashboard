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
        url = item_url(item)
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


def item_url(item: ElementTree.Element) -> str:
    """Чистая ссылка из guid, а если её нет, то link (у Хабра в link есть utm-метки)."""
    guid = item.find('guid')
    if guid is not None and guid.get('isPermaLink', 'true') == 'true' and guid.text:
        return guid.text.strip()
    return item.findtext('link', '').strip()
