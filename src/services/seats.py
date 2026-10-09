"""Бизнес-логика получения свободных мест с кэшем."""

import logging
import time
from uuid import UUID

from src.client.events_provider import EventsProviderClient
from src.services.exceptions import EventNotFoundError, EventNotPublishedError
from src.services.protocols import EventRepositoryProtocol

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 30


class SeatsService:
    """Сервис получения свободных мест с in-memory кэшем (30 сек)."""

    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepositoryProtocol,
    ) -> None:
        self._client = client
        self._events = events
        # кэш: {event_id: (timestamp, [seats])}
        self._cache: dict[str, tuple[float, list[str]]] = {}

    async def get_available_seats(self, event_id: UUID) -> list[str]:
        """Получить список свободных мест (с кэшем 30 сек)."""
        # Проверяем, что событие есть и опубликовано — чтобы не словить 500 от API
        event = await self._events.get(event_id)
        if event is None:
            raise EventNotFoundError(f"Событие {event_id} не найдено")
        if event.status != "published":
            raise EventNotPublishedError(
                f"Событие {event_id} не опубликовано, регистрация запрещена"
            )

        key = str(event_id)
        now = time.time()

        cached = self._cache.get(key)
        if cached is not None:
            ts, seats = cached
            if now - ts < CACHE_TTL_SECONDS:
                logger.debug("Возвращаем закэшированные места для %s", event_id)
                return seats

        # Запрашиваем у внешнего API
        seats = await self._client.seats(key)
        self._cache[key] = (now, seats)
        logger.info("Получено %d мест для события %s", len(seats), event_id)
        return seats

    def invalidate(self, event_id: UUID) -> None:
        """Сбросить кэш для события (например, после регистрации)."""
        self._cache.pop(str(event_id), None)
