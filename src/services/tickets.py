"""Бизнес-логика регистрации и отмены билетов."""

import logging
from uuid import UUID

from src.client.events_provider import EventsProviderError
from src.models.enums import EventStatus
from src.services.exceptions import (
    EventNotFoundError,
    EventNotPublishedError,
    SeatNotAvailableError,
    TicketNotFoundError,
)
from src.services.protocols import (
    EventRepositoryProtocol,
    EventsProviderClientProtocol,
    TicketRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class CreateTicketUsecase:
    """Регистрация на событие.

    1. Проверяем, что событие есть локально.
    2. Проверяем, что оно published.
    3. Проверяем, что место свободно (через внешний API).
    4. Регистрируем во внешнем API, получаем ticket_id.
    5. Сохраняем билет в локальную БД.
    """

    def __init__(
        self,
        client: EventsProviderClientProtocol,
        events: EventRepositoryProtocol,
        tickets: TicketRepositoryProtocol,
    ) -> None:
        self._client = client
        self._events = events
        self._tickets = tickets

    async def do(
        self,
        event_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> str:
        """Выполнить use case. Возвращает ticket_id."""
        event = await self._events.get(event_id)
        if event is None:
            raise EventNotFoundError(f"Событие {event_id} не найдено")

        if event.status != EventStatus.PUBLISHED:
            raise EventNotPublishedError(
                f"Событие {event_id} не опубликовано (status={event.status})"
            )

        # Проверяем, что место свободно через внешний API
        available = await self._client.seats(str(event_id))
        if seat not in available:
            raise SeatNotAvailableError(f"Место {seat} недоступно")

        # Регистрируем во внешнем API
        try:
            ticket_id = await self._client.register(
                event_id=str(event_id),
                first_name=first_name,
                last_name=last_name,
                seat=seat,
                email=email,
            )
        except EventsProviderError as exc:
            logger.error("Ошибка регистрации во внешнем API: %s", exc)
            raise SeatNotAvailableError(f"Не удалось зарегистрироваться: {exc}") from exc

        # Сохраняем билет в локальную БД
        await self._tickets.create(
            event_id=event_id,
            ticket_id=UUID(ticket_id),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )

        logger.info(
            "Зарегистрирован билет %s на событие %s, место %s",
            ticket_id,
            event_id,
            seat,
        )
        return ticket_id


class CancelTicketUsecase:
    """Отмена регистрации.

    1. Проверяем, что билет есть локально.
    2. Отменяем во внешнем API.
    3. Удаляем билет из локальной БД.
    """

    def __init__(
        self,
        client: EventsProviderClientProtocol,
        tickets: TicketRepositoryProtocol,
    ) -> None:
        self._client = client
        self._tickets = tickets

    async def do(self, ticket_id: UUID) -> bool:
        """Отменить билет. Возвращает True при успехе."""
        ticket = await self._tickets.get_by_ticket_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(f"Билет {ticket_id} не найден")

        await self._client.unregister(
            event_id=str(ticket.event_id),
            ticket_id=str(ticket_id),
        )

        await self._tickets.delete_by_ticket_id(ticket_id)
        logger.info("Отменён билет %s", ticket_id)
        return True
