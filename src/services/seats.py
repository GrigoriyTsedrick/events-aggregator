"""Бизнес-логика получения свободных мест с кэшем."""
import logging
from uuid import UUID

from src.client.events_provider import EventsProviderClient
from src.models.enums import EventStatus
from src.services.cache import cache
from src.services.exceptions import EventNotFoundError, EventNotPublishedError
from src.services.protocols import EventRepositoryProtocol

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 30


class SeatsService:
    """Сервис получения свободных мест с in-memory кэшем (30 сек).

    Кэш — глобальный (module-level), поэтому работает между запросами.
    """

    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepositoryProtocol,
    ) -> None:
        self._client = client
        self._events = events

    async def get_available_seats(self, event_id: UUID) -> list[str]:
        """Получить список свободных мест (с кэшем 30 сек)."""
        event = await self._events.get(event_id)
        if event is None:
            raise EventNotFoundError(f"Событие {event_id} не найдено")
        if event.status != EventStatus.PUBLISHED:
            raise EventNotPublishedError(
                f"Событие {event_id} не опубликовано, регистрация запрещена"
            )

        key = f"seats:{event_id}"

        cached = cache.get(key, CACHE_TTL_SECONDS)
        if cached is not None:
            logger.debug("Возвращаем закэшированные места для %s", event_id)
            return cached

        seats = await self._client.seats(str(event_id))
        cache.set(key, seats)
        logger.info("Получено %d мест для события %s", len(seats), event_id)
        return seats

    def invalidate(self, event_id: UUID) -> None:
        """Сбросить кэш для события (после регистрации/отмены)."""
        cache.invalidate(f"seats:{event_id}")
