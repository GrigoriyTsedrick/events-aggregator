"""Простой in-memory кэш с TTL.

Вынесен на уровень модуля — singleton, живёт всё время работы приложения.
Это решает проблему, когда SeatsService создаётся на каждый запрос
и его собственный self._cache не сохраняется между запросами.
"""

import time
from typing import Any


class MemoryCache:
    """In-memory кэш с TTL."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str, ttl: float) -> Any | None:
        """Вернуть значение, если оно не протухло, иначе None."""
        item = self._store.get(key)
        if item is None:
            return None
        ts, value = item
        if time.time() - ts > ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        """Записать значение с текущим временем."""
        self._store[key] = (time.time(), value)

    def invalidate(self, key: str) -> None:
        """Удалить значение."""
        self._store.pop(key, None)


# Глобальный singleton — один на всё приложение
cache = MemoryCache()
