"""Точка входа FastAPI."""
from fastapi import FastAPI

from src.api.v1.router import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
)

app.include_router(api_router)
