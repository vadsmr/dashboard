import datetime as dt

from fastapi import APIRouter, HTTPException, status

from app.deps import RatesServiceDep
from app.schemas.rates import CurrencyRateDTO
from app.services.rates import SourceUnavailableError

router = APIRouter(tags=['rates'])


@router.get('/rates')
async def list_rates(service: RatesServiceDep, date: dt.date) -> list[CurrencyRateDTO]:
    return await service.get_rates(date)


@router.post('/rates/sync')
async def sync_rates(service: RatesServiceDep, date: dt.date | None = None) -> dict[str, int]:
    try:
        saved = await service.collect(date=date)
    except SourceUnavailableError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {'saved': saved}
