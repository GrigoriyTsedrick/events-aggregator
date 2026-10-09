"""Схемы площадки."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaceShort(BaseModel):
    """Краткая информация о площадке (для списка событий)."""

    id: UUID
    name: str
    city: str
    address: str

    model_config = ConfigDict(from_attributes=True)


class PlaceDetail(PlaceShort):
    """Полная информация о площадке."""

    seats_pattern: str
