"""Репозиторий для метаданных синхронизации."""

from sqlalchemy import select

from src.models.sync_metadata import SyncMetadata
from src.repositories.base import BaseRepository


class SyncRepository(BaseRepository[SyncMetadata]):
    """Репозиторий метаданных синхронизации."""

    model = SyncMetadata

    async def get_singleton(self) -> SyncMetadata:
        """Получить единственную запись метаданных (создать, если нет)."""
        result = await self.session.execute(select(SyncMetadata).limit(1))
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = SyncMetadata(sync_status="idle")
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
        return obj
