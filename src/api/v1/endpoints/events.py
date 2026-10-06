"""Эндпоинты для работы с событиями."""
from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status

from src.api.deps import EventServiceDep, SeatsServiceDep
from src.schemas.event import EventDetail, EventListResponse
from src.schemas.seats import SeatsResponse
from src.services.exceptions import (
    EventNotFoundError,
    EventNotPublishedError,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventListResponse)
async def list_events(
    request: Request,
    service: EventServiceDep,
    date_from: Annotated[date | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> EventListResponse:
    """Список событий с фильтром по дате и пагинацией."""
    events, total = await service.list_events(
        date_from=date_from,
        page=page,
        page_size=page_size,
    )

    base_url = str(request.base_url).rstrip("/")
    next_url = None
    previous_url = None

    if page * page_size < total:
        next_url = f"{base_url}/api/events?page={page + 1}&page_size={page_size}"
    if page > 1:
        previous_url = f"{base_url}/api/events?page={page - 1}&page_size={page_size}"

    return EventListResponse(
        count=total,
        next=next_url,
        previous=previous_url,
        results=events,
    )


@router.get("/{event_id}", response_model=EventDetail)
async def get_event(event_id: UUID, service: EventServiceDep) -> EventDetail:
    """Детали события по id."""
    event = await service.get_by_id(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие не найдено",
        )
    return event


@router.get("/{event_id}/seats", response_model=SeatsResponse)
async def get_seats(event_id: UUID, service: SeatsServiceDep) -> SeatsResponse:
    """Список свободных мест на событии (кэш 30 сек)."""
    try:
        seats = await service.get_available_seats(event_id)
    except EventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EventNotPublishedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return SeatsResponse(event_id=event_id, available_seats=seats)
