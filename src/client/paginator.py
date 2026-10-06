"""Итератор по всем страницам событий (cursor-based пагинация)."""
import logging
from collections.abc import AsyncIterator
from typing import Any

from src.client.events_provider import EventsProviderClient

logger = logging.getLogger(__name__)


class EventsPaginator:
    """Итератор по всем событиям из Events Provider API.

    Использование:
        async for event in EventsPaginator(client, changed_at="2000-01-01"):
            # event — словарь с данными события
            ...
    """

    def __init__(
        self,
        client: EventsProviderClient,
        changed_at: str,
    ) -> None:
        self._client = client
        self._changed_at = changed_at
        self._next_url: str | None = None
        self._first_page_done = False

    def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        return self

    async def __anext__(self) -> dict[str, Any]:
        """Вернуть следующее событие или StopAsyncIteration."""
        # Если накопитель пуст — грузим страницу
        if not hasattr(self, "_buffer") or not self._buffer:
            await self._load_next_page()
            if not self._buffer:
                raise StopAsyncIteration
        return self._buffer.pop(0)

    async def _load_next_page(self) -> None:
        """Загрузить следующую страницу и положить события в буфер."""
        if self._first_page_done and self._next_url is None:
            self._buffer: list[dict] = []
            return

        if not self._first_page_done:
            data = await self._client.events(changed_at=self._changed_at)
            self._first_page_done = True
        else:
            data = await self._client.events_by_url(self._next_url)

        self._buffer = data.get("results", [])
        self._next_url = data.get("next")

        logger.info(
            "Загружена страница: %d событий, next=%s",
            len(self._buffer),
            bool(self._next_url),
        )
