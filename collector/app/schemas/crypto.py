import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CryptoPriceDTO(BaseModel):
    coin: str
    currency: str
    date: dt.date
    price: Decimal

    model_config = ConfigDict(from_attributes=True)
