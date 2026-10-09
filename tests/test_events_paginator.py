"""Тесты для EventsPaginator с моками клиента."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.client.paginator import EventsPaginator


def make_client(
    events_return: dict,
    events_by_url_return: dict | None = None,
) -> MagicMock:
    """Создать mock-клиент с настраиваемыми ответами."""
    client = MagicMock()
    client.events = AsyncMock(return_value=events_return)
    client.events_by_url = AsyncMock(
        return_value=events_by_url_return if events_by_url_return else events_return
    )
    return client


@pytest.mark.asyncio
async def test_single_page() -> None:
    """Одна страница — все события возвращаются."""
    client = make_client(
        events_return={
            "next": None,
            "results": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
        }
    )

    paginator = EventsPaginator(client, changed_at="2000-01-01")
    results = [event async for event in paginator]

    assert results == [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    client.events.assert_awaited_once_with(changed_at="2000-01-01")
    client.events_by_url.assert_not_awaited()


@pytest.mark.asyncio
async def test_multiple_pages() -> None:
    """Несколько страниц — все события собираются."""
    page1 = {
        "next": "http://test.local/api/events/?cursor=abc",
        "results": [{"id": "1"}, {"id": "2"}],
    }
    page2 = {
        "next": None,
        "results": [{"id": "3"}],
    }

    client = MagicMock()
    client.events = AsyncMock(return_value=page1)
    client.events_by_url = AsyncMock(return_value=page2)

    paginator = EventsPaginator(client, changed_at="2000-01-01")
    results = [event async for event in paginator]

    assert results == [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    client.events.assert_awaited_once_with(changed_at="2000-01-01")
    client.events_by_url.assert_awaited_once_with("http://test.local/api/events/?cursor=abc")


@pytest.mark.asyncio
async def test_empty_response_stops_iteration() -> None:
    """Пустая страница — StopAsyncIteration."""
    client = make_client(events_return={"next": None, "results": []})

    paginator = EventsPaginator(client, changed_at="2000-01-01")
    results = [event async for event in paginator]

    assert results == []


@pytest.mark.asyncio
async def test_next_url_used_as_is() -> None:
    """Paginator использует next-url как есть (не собирает сам)."""
    full_url = "http://test.local/api/events/?changed_at=2000-01-01&cursor=xyz"
    page1 = {"next": full_url, "results": [{"id": "1"}]}
    page2 = {"next": None, "results": [{"id": "2"}]}

    client = MagicMock()
    client.events = AsyncMock(return_value=page1)
    client.events_by_url = AsyncMock(return_value=page2)

    paginator = EventsPaginator(client, changed_at="2000-01-01")
    _ = [event async for event in paginator]

    client.events_by_url.assert_awaited_once_with(full_url)
