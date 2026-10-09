"""Схемы свободных мест."""

from uuid import UUID

from pydantic import BaseModel


class SeatsResponse(BaseModel):
    """Список свободных мест на событии."""

    event_id: UUID
    available_seats: list[str]
