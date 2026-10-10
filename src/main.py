"""Точка входа FastAPI."""

import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.api.errors import validation_exception_handler
from src.api.v1.router import api_router
from src.core.config import settings
from src.workers.sync_worker import run_periodic_sync


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: старт и остановка фонового воркера."""
    sync_task = asyncio.create_task(run_periodic_sync(settings.sync_interval_hours))
    yield
    sync_task.cancel()
    with suppress(asyncio.CancelledError):
        await sync_task


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(api_router)
