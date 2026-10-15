from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

router = APIRouter()


@router.get('/health')
async def health(
    session: Annotated[AsyncSession, Depends(get_session)],
    response: Response,
) -> dict[str, str]:
    try:
        await session.execute(text('SELECT 1'))
        return {'status': 'ok'}
    except (SQLAlchemyError, OSError):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {'status': 'error'}
