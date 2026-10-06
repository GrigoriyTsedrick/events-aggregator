"""Кастомные обработчики ошибок FastAPI.

По требованиям LMS все ошибки валидации должны возвращаться как 400,
а не 422 (стандарт FastAPI).
"""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Перехватывает ошибки валидации Pydantic и возвращает 400.

    Сохраняет структуру ответа {"detail": [...]} — как у стандартного 422,
    но с кодом 400 (требование LMS).
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )
