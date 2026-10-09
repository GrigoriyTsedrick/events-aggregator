"""Модель регистрации (билета)."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


def get_utc_now() -> datetime:
    """Текущее время в UTC."""
    return datetime.now(UTC)


class Ticket(Base):
    """Регистрация участника на событие."""

    __tablename__ = "tickets"
    __table_args__ = (UniqueConstraint("event_id", "seat", name="uq_event_seat"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticket_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    seat: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    event = relationship("Event", back_populates="tickets")
