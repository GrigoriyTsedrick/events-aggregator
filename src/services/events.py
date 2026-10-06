"""Бизнес-логика получения событий."""
from datetime import date

from src.models.event import Event
from src.repositories.event import EventRepository


class EventService:
    """Сервис работы с событиями."""

    def __init__(self, events: EventRepository) -> None:
        self._events = events

    async def get_by_id(self, event_id) -> Event | None:
        """Получить событие с подгруженной площадкой."""
        return await self._events.get_with_place(event_id)

    async def list_events(
        self,
        date_from: date | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Event], int]:
        """Список событий с фильтром и пагинацией.

        Возвращает (события, общее количество).
        """
        return await self._events.list_with_filters(
            date_from=date_from,
            page=page,
            page_size=page_size,
        )
