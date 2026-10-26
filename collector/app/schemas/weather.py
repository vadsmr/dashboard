import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class WeatherDTO(BaseModel):
    city: str
    date: dt.date
    temp_max: Decimal
    temp_min: Decimal
    precipitation: Decimal

    model_config = ConfigDict(from_attributes=True)


class Location(BaseModel):
    city: str
    latitude: float
    longitude: float
