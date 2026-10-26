import datetime as dt

from fastapi import APIRouter, HTTPException, status

from app.deps import WeatherServiceDep
from app.schemas.weather import WeatherDTO
from app.services.errors import SourceUnavailableError

router = APIRouter(tags=['weather'])


@router.get('/weather')
async def get_forecast(
    service: WeatherServiceDep, date_from: dt.date | None = None
) -> list[WeatherDTO]:
    return await service.get_forecast(date_from or dt.date.today())


@router.post('/weather/sync')
async def sync_weather(service: WeatherServiceDep) -> dict[str, int]:
    try:
        saved = await service.collect()
    except SourceUnavailableError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {'saved': saved}
