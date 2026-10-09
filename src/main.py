"""Точка входа FastAPI."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.api.errors import validation_exception_handler
from src.api.v1.router import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
)

# Перехватываем ошибки валидации и возвращаем 400 вместо 422
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(api_router)
