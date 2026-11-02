import datetime as dt

from pydantic import BaseModel, ConfigDict


class NewsItemDTO(BaseModel):
    feed: str
    title: str
    url: str
    published_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
