"""Базовый репозиторий с общими методами."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий: get, create, update, delete."""

    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, obj_id: UUID) -> ModelType | None:
        """Найти запись по id."""
        return await self.session.get(self.model, obj_id)

    async def list(self) -> list[ModelType]:
        """Получить все записи."""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        """Создать запись."""
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType, **kwargs) -> ModelType:
        """Обновить существующую запись."""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
