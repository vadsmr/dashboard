import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CurrencyRateDTO(BaseModel):
    code: str
    date: dt.date
    rate: Decimal

    model_config = ConfigDict(from_attributes=True)
