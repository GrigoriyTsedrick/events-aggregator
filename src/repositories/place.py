"""Репозиторий для работы с площадками."""

from sqlalchemy.dialects.postgresql import insert

from src.models.place import Place
from src.repositories.base import BaseRepository


class PlaceRepository(BaseRepository[Place]):
    """Репозиторий площадок."""

    model = Place

    async def upsert(self, data: dict) -> None:
        """Вставить или обновить площадку по id (ON CONFLICT DO UPDATE)."""
        stmt = insert(Place).values(**data)
        update_fields = {
            "name": stmt.excluded.name,
            "city": stmt.excluded.city,
            "address": stmt.excluded.address,
            "seats_pattern": stmt.excluded.seats_pattern,
            "changed_at": stmt.excluded.changed_at,
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_=update_fields,
        )
        await self.session.execute(stmt)
        await self.session.commit()
