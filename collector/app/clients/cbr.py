import datetime as dt
from decimal import Decimal
from xml.etree import ElementTree

import httpx

from app.schemas.rates import CurrencyRateDTO


class CbrClient:
    def __init__(self, http: httpx.AsyncClient, base_url: str) -> None:
        self.base_url = base_url
        self.http = http

    async def fetch_daily(self, date: dt.date | None = None) -> list[CurrencyRateDTO]:
        response = await self.http.get(
            f'{self.base_url}/scripts/XML_daily.asp',
            params={'date': date.strftime('%d/%m/%Y')} if date else None,
        )
        response.raise_for_status()
        return parse_daily(response.content)


def parse_daily(content: bytes) -> list[CurrencyRateDTO]:
    root = ElementTree.fromstring(content)

    date = dt.datetime.strptime(root.attrib['Date'], '%d.%m.%Y').date()
    result = []
    for item in root.iter('Valute'):
        code = item.findtext('CharCode')
        value = item.findtext('Value', '0')
        nominal = item.findtext('Nominal', '1')
        rate = Decimal(value.replace(',', '.')) / int(nominal)
        result.append(CurrencyRateDTO(code=code, date=date, rate=rate))

    return result
