"""Схемы события."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.schemas.place import PlaceDetail, PlaceShort


class EventShort(BaseModel):
    """Краткая информация о событии (для списка)."""

    id: UUID
    name: str
    place: PlaceShort
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int

    model_config = ConfigDict(from_attributes=True)


class EventDetail(BaseModel):
    """Полная информация о событии."""

    id: UUID
    name: str
    place: PlaceDetail
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    """Ответ со списком событий и пагинацией."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[EventShort]
