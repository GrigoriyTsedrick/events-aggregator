"""Фоновый воркер периодической синхронизации событий."""
import asyncio
import logging

from src.client.events_provider import EventsProviderClient
from src.core.config import settings
from src.core.db import async_session_maker
from src.repositories.event import EventRepository
from src.repositories.place import PlaceRepository
from src.repositories.sync import SyncRepository
from src.services.sync import SyncService

logger = logging.getLogger(__name__)


async def _run_sync_once() -> dict:
    """Выполнить одну синхронизацию с новой сессией и клиентом."""
    async with (
        EventsProviderClient(
            base_url=settings.events_provider_url,
            api_key=settings.events_provider_api_key,
        ) as client,
        async_session_maker() as session,
    ):
        service = SyncService(
            client=client,
            events=EventRepository(session),
            places=PlaceRepository(session),
            sync_meta=SyncRepository(session),
        )
        return await service.sync()


async def run_periodic_sync(interval_hours: int) -> None:
    """Бесконечный цикл периодической синхронизации.

    Запускается один раз в lifespan FastAPI как asyncio.Task.
    Останавливается через отмену задачи при shutdown.
    """
    interval_seconds = interval_hours * 3600
    logger.info(
        "Периодическая синхронизация запущена (интервал %d ч)", interval_hours
    )

    while True:
        try:
            logger.info("Периодическая синхронизация: старт")
            result = await _run_sync_once()
            logger.info("Периодическая синхронизация: %s", result)
        except asyncio.CancelledError:
            logger.info("Периодическая синхронизация остановлена")
            raise
        except Exception as exc:  # noqa: BLE001 — воркер не должен падать
            logger.exception("Ошибка периодической синхронизации: %s", exc)

        await asyncio.sleep(interval_seconds)
