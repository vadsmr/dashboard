import datetime as dt
from decimal import Decimal

from pydantic import BaseModel


class CurrencyRateDTO(BaseModel):
    code: str
    date: dt.date
    rate: Decimal
