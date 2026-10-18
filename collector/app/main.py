from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api import health
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_async_engine(get_settings().database_url)
    app.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with httpx.AsyncClient(timeout=10) as http:
        app.state.http = http
        yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title='Collector', lifespan=lifespan)
    app.include_router(health.router)
    return app


app = create_app()
