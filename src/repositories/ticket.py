"""Репозиторий для работы с билетами."""

from uuid import UUID

from sqlalchemy import select

from src.models.ticket import Ticket
from src.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    """Репозиторий билетов."""

    model = Ticket

    async def get_by_ticket_id(self, ticket_id: UUID) -> Ticket | None:
        """Найти билет по внешнему ticket_id."""
        result = await self.session.execute(select(Ticket).where(Ticket.ticket_id == ticket_id))
        return result.scalar_one_or_none()

    async def delete_by_ticket_id(self, ticket_id: UUID) -> bool:
        """Удалить билет по ticket_id. Возвращает True, если что-то удалено."""
        ticket = await self.get_by_ticket_id(ticket_id)
        if ticket is None:
            return False
        await self.session.delete(ticket)
        await self.session.commit()
        return True
