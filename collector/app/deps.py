from typing import Annotated

import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.cbr import CbrClient
from app.config import get_settings
from app.db.session import get_session
from app.services.rates import RatesService


def get_http(request: Request) -> httpx.AsyncClient:
    http: httpx.AsyncClient = request.app.state.http
    return http


def get_cbr_client(http: Annotated[httpx.AsyncClient, Depends(get_http)]) -> CbrClient:
    return CbrClient(http, get_settings().cbr_base_url)


def get_rates_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    client: Annotated[CbrClient, Depends(get_cbr_client)],
) -> RatesService:
    return RatesService(session, client)


RatesServiceDep = Annotated[RatesService, Depends(get_rates_service)]
