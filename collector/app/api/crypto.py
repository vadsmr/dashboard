import datetime as dt

from fastapi import APIRouter, HTTPException, status

from app.deps import CryptoServiceDep
from app.schemas.crypto import CryptoPriceDTO
from app.services.errors import SourceUnavailableError

router = APIRouter(tags=['crypto'])


@router.get('/crypto_prices')
async def get_prices(
    service: CryptoServiceDep, date_from: dt.date | None = None
) -> list[CryptoPriceDTO]:
    return await service.get_prices(date_from or dt.date.today())


@router.post('/crypto/sync')
async def sync_prices(service: CryptoServiceDep) -> dict[str, int]:
    try:
        saved = await service.collect()
    except SourceUnavailableError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {'saved': saved}
