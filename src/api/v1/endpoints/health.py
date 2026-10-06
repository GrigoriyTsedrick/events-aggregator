"""Health-check эндпоинт."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Проверка доступности сервиса."""
    return {"status": "ok"}
