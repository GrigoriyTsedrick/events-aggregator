"""Эндпоинты для регистрации и отмены."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CancelTicketUsecaseDep, CreateTicketUsecaseDep
from src.schemas.ticket import CancelResponse, TicketCreate, TicketResponse
from src.services.exceptions import (
    EventNotFoundError,
    EventNotPublishedError,
    SeatNotAvailableError,
    TicketNotFoundError,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate,
    usecase: CreateTicketUsecaseDep,
) -> TicketResponse:
    """Регистрация на событие."""
    try:
        ticket_id = await usecase.do(
            event_id=payload.event_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            seat=payload.seat,
        )
    except EventNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EventNotPublishedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SeatNotAvailableError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return TicketResponse(ticket_id=UUID(ticket_id))


@router.delete("/{ticket_id}", response_model=CancelResponse)
async def cancel_ticket(
    ticket_id: UUID,
    usecase: CancelTicketUsecaseDep,
) -> CancelResponse:
    """Отмена регистрации."""
    try:
        success = await usecase.do(ticket_id)
    except TicketNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return CancelResponse(success=success)
