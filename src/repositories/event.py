"""Репозиторий для работы с событиями."""

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from src.models.event import Event
from src.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """Репозиторий событий."""

    model = Event

    async def upsert(self, data: dict) -> None:
        """Вставить или обновить событие по id."""
        stmt = insert(Event).values(**data)
        update_fields = {
            "name": stmt.excluded.name,
            "place_id": stmt.excluded.place_id,
            "event_time": stmt.excluded.event_time,
            "registration_deadline": stmt.excluded.registration_deadline,
            "status": stmt.excluded.status,
            "number_of_visitors": stmt.excluded.number_of_visitors,
            "changed_at": stmt.excluded.changed_at,
            "status_changed_at": stmt.excluded.status_changed_at,
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_=update_fields,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_with_place(self, event_id) -> Event | None:
        """Получить событие вместе с площадкой (eager load)."""
        result = await self.session.execute(
            select(Event).where(Event.id == event_id).options(selectinload(Event.place))
        )
        return result.scalar_one_or_none()

    async def list_with_filters(
        self,
        date_from: date | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Event], int]:
        """Список событий с фильтром по дате и пагинацией.

        Возвращает (список событий, общее количество).
        """
        query = select(Event).options(selectinload(Event.place))
        count_query = select(func.count()).select_from(Event)

        if date_from is not None:
            dt_from = datetime.combine(date_from, datetime.min.time())
            query = query.where(Event.event_time >= dt_from)
            count_query = count_query.where(Event.event_time >= dt_from)

        total = (await self.session.execute(count_query)).scalar_one()

        query = query.order_by(Event.event_time).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total
