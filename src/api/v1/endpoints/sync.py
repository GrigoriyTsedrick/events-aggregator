"""Эндпоинт ручного запуска синхронизации."""
from fastapi import APIRouter

from src.api.deps import SyncServiceDep

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/trigger")
async def trigger_sync(service: SyncServiceDep) -> dict:
    """Запустить синхронизацию вручную."""
    result = await service.sync()
    return result
