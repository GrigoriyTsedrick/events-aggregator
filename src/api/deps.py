"""Зависимости FastAPI: сессия, репозитории, сервисы."""
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.client.events_provider import EventsProviderClient
from src.core.config import settings
from src.core.db import get_async_session
from src.repositories import (
    EventRepository,
    PlaceRepository,
    SyncRepository,
    TicketRepository,
)
from src.services import (
    CancelTicketUsecase,
    CreateTicketUsecase,
    EventService,
    SeatsService,
    SyncService,
)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_events_provider_client() -> AsyncIterator[EventsProviderClient]:
    """Создаёт httpx-клиент на время запроса и закрывает после."""
    client = EventsProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.events_provider_api_key,
    )
    try:
        yield client
    finally:
        await client.close()


ClientDep = Annotated[EventsProviderClient, Depends(get_events_provider_client)]


# === Репозитории ===

def get_event_repository(session: SessionDep) -> EventRepository:
    return EventRepository(session)


def get_place_repository(session: SessionDep) -> PlaceRepository:
    return PlaceRepository(session)


def get_ticket_repository(session: SessionDep) -> TicketRepository:
    return TicketRepository(session)


def get_sync_repository(session: SessionDep) -> SyncRepository:
    return SyncRepository(session)


EventRepoDep = Annotated[EventRepository, Depends(get_event_repository)]
PlaceRepoDep = Annotated[PlaceRepository, Depends(get_place_repository)]
TicketRepoDep = Annotated[TicketRepository, Depends(get_ticket_repository)]
SyncRepoDep = Annotated[SyncRepository, Depends(get_sync_repository)]


# === Сервисы ===

def get_event_service(events: EventRepoDep) -> EventService:
    return EventService(events)


def get_seats_service(
    client: ClientDep,
    events: EventRepoDep,
) -> SeatsService:
    return SeatsService(client, events)


def get_sync_service(
    client: ClientDep,
    events: EventRepoDep,
    places: PlaceRepoDep,
    sync_repo: SyncRepoDep,
) -> SyncService:
    return SyncService(client, events, places, sync_repo)


def get_create_ticket_usecase(
    client: ClientDep,
    events: EventRepoDep,
    tickets: TicketRepoDep,
) -> CreateTicketUsecase:
    return CreateTicketUsecase(client, events, tickets)


def get_cancel_ticket_usecase(
    client: ClientDep,
    tickets: TicketRepoDep,
) -> CancelTicketUsecase:
    return CancelTicketUsecase(client, tickets)


EventServiceDep = Annotated[EventService, Depends(get_event_service)]
SeatsServiceDep = Annotated[SeatsService, Depends(get_seats_service)]
SyncServiceDep = Annotated[SyncService, Depends(get_sync_service)]
CreateTicketUsecaseDep = Annotated[CreateTicketUsecase, Depends(get_create_ticket_usecase)]
CancelTicketUsecaseDep = Annotated[CancelTicketUsecase, Depends(get_cancel_ticket_usecase)]
