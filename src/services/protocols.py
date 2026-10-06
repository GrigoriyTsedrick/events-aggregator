"""Протоколы для бизнес-логики.

Бизнес-логика не должна знать про конкретные реализации БД и HTTP-клиента —
она работает через эти протоколы.
"""
from typing import Protocol

from src.models.event import Event


class EventsProviderClientProtocol(Protocol):
    """Интерфейс клиента внешнего API."""

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        seat: str,
        email: str,
    ) -> str: ...

    async def unregister(self, event_id: str, ticket_id: str) -> bool: ...

    async def seats(self, event_id: str) -> list[str]: ...


class EventRepositoryProtocol(Protocol):
    """Интерфейс репозитория событий."""

    async def get(self, event_id) -> Event | None: ...

    async def get_with_place(self, event_id) -> Event | None: ...


class TicketRepositoryProtocol(Protocol):
    """Интерфейс репозитория билетов."""

    async def create(self, **kwargs): ...

    async def get_by_ticket_id(self, ticket_id): ...

    async def delete_by_ticket_id(self, ticket_id) -> bool: ...
