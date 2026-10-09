"""Модель события."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class Event(Base):
    """Мероприятие."""

    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)

    place_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("places.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    number_of_visitors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    place = relationship("Place", back_populates="events")
    tickets = relationship("Ticket", back_populates="event")
