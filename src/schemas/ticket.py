"""Схемы билета."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TicketCreate(BaseModel):
    """Тело запроса на регистрацию."""

    event_id: UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    seat: str = Field(..., min_length=1, max_length=20)


class TicketResponse(BaseModel):
    """Ответ при успешной регистрации."""

    ticket_id: UUID


class CancelResponse(BaseModel):
    """Ответ при отмене регистрации."""

    success: bool
