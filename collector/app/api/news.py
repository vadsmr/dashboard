from typing import Annotated

from fastapi import APIRouter, Query

from app.deps import NewsServiceDep
from app.schemas.news import NewsItemDTO

router = APIRouter(tags=['news'])


@router.get('/news')
async def get_news(
    service: NewsServiceDep, limit: Annotated[int, Query(ge=1, le=100)] = 20
) -> list[NewsItemDTO]:
    return await service.get_latest(limit)


@router.post('/news/sync')
async def sync_news(service: NewsServiceDep) -> dict[str, int]:
    return {'added': await service.collect()}
