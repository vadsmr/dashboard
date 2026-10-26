import datetime as dt
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CurrencyRate(Base):
    __tablename__ = 'currency_rates'
    __table_args__ = (UniqueConstraint('code', 'date'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(3))
    date: Mapped[dt.date] = mapped_column(Date())
    rate: Mapped[Decimal] = mapped_column(Numeric(14, 6))
    fetched_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class WeatherDaily(Base):
    __tablename__ = 'weather_daily'
    __table_args__ = (UniqueConstraint('city', 'date'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(50))
    date: Mapped[dt.date] = mapped_column(Date())
    temp_max: Mapped[Decimal] = mapped_column(Numeric(4, 1))
    temp_min: Mapped[Decimal] = mapped_column(Numeric(4, 1))
    precipitation: Mapped[Decimal] = mapped_column(Numeric(5, 1))
    fetched_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
