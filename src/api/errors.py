"""Обработчики ошибок FastAPI: превращаем 422 в 400."""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Обработчик ошибок валидации Pydantic.

    По умолчанию FastAPI возвращает 422.
    Тесты LMS ожидают 400 — переопределяем.

    Ответ оставляем в том же формате (detail со списком ошибок),
    только меняем код с 422 на 400.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )
