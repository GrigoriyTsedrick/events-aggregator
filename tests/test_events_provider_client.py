"""Тесты для EventsProviderClient с моками HTTP."""

from unittest.mock import AsyncMock

import httpx
import pytest

from src.client.events_provider import EventsProviderClient, EventsProviderError


@pytest.fixture
def client() -> EventsProviderClient:
    """Клиент с замоканным httpx.AsyncClient."""
    return EventsProviderClient(base_url="http://test.local", api_key="test-key")


def make_response(
    status_code: int,
    json_data: dict | list | None = None,
) -> httpx.Response:
    """Создать httpx.Response с нужным кодом и JSON."""
    response = httpx.Response(
        status_code=status_code,
        json=json_data,
        request=httpx.Request("GET", "http://test.local"),
    )
    return response


@pytest.mark.asyncio
async def test_events_returns_data(client: EventsProviderClient) -> None:
    """events() возвращает словарь с results."""
    payload = {
        "next": None,
        "previous": None,
        "results": [{"id": "1", "name": "Test"}],
    }
    client._client.get = AsyncMock(return_value=make_response(200, payload))

    result = await client.events(changed_at="2000-01-01")

    assert result == payload
    client._client.get.assert_awaited_once()
    _, kwargs = client._client.get.call_args
    assert kwargs["params"] == {"changed_at": "2000-01-01"}


@pytest.mark.asyncio
async def test_events_with_cursor(client: EventsProviderClient) -> None:
    """events() передаёт cursor, если он указан."""
    client._client.get = AsyncMock(return_value=make_response(200, {"results": []}))

    await client.events(changed_at="2026-01-01", cursor="abc")

    _, kwargs = client._client.get.call_args
    assert kwargs["params"] == {"changed_at": "2026-01-01", "cursor": "abc"}


@pytest.mark.asyncio
async def test_events_raises_on_error(client: EventsProviderClient) -> None:
    """events() выбрасывает EventsProviderError при 4xx."""
    client._client.get = AsyncMock(return_value=make_response(400, {"detail": "bad"}))

    with pytest.raises(EventsProviderError):
        await client.events(changed_at="2000-01-01")


@pytest.mark.asyncio
async def test_events_by_url(client: EventsProviderClient) -> None:
    """events_by_url() забирает страницу по прямому URL."""
    payload = {"next": None, "results": [{"id": "2"}]}
    client._client.get = AsyncMock(return_value=make_response(200, payload))

    result = await client.events_by_url("http://test.local/api/events/?cursor=xyz")

    assert result == payload


@pytest.mark.asyncio
async def test_seats_returns_list(client: EventsProviderClient) -> None:
    """seats() возвращает список мест."""
    client._client.get = AsyncMock(return_value=make_response(200, {"seats": ["A1", "A2"]}))

    seats = await client.seats(event_id="evt-1")

    assert seats == ["A1", "A2"]


@pytest.mark.asyncio
async def test_seats_returns_empty_if_no_key(client: EventsProviderClient) -> None:
    """seats() возвращает пустой список, если в ответе нет ключа seats."""
    client._client.get = AsyncMock(return_value=make_response(200, {}))

    seats = await client.seats(event_id="evt-1")

    assert seats == []


@pytest.mark.asyncio
async def test_register_returns_ticket_id(client: EventsProviderClient) -> None:
    """register() возвращает ticket_id."""
    client._client.post = AsyncMock(return_value=make_response(201, {"ticket_id": "ticket-123"}))

    ticket_id = await client.register(
        event_id="evt-1",
        first_name="Иван",
        last_name="Иванов",
        seat="A1",
        email="ivan@example.com",
    )

    assert ticket_id == "ticket-123"
    client._client.post.assert_awaited_once()
    _, kwargs = client._client.post.call_args
    assert kwargs["json"]["seat"] == "A1"
    assert kwargs["json"]["email"] == "ivan@example.com"


@pytest.mark.asyncio
async def test_register_raises_on_400(client: EventsProviderClient) -> None:
    """register() выбрасывает ошибку при 400 (место занято)."""
    client._client.post = AsyncMock(
        return_value=make_response(400, ["This ticket is not available"])
    )

    with pytest.raises(EventsProviderError):
        await client.register(
            event_id="evt-1",
            first_name="Иван",
            last_name="Иванов",
            seat="A1",
            email="ivan@example.com",
        )


@pytest.mark.asyncio
async def test_unregister_returns_true(client: EventsProviderClient) -> None:
    """unregister() возвращает True при успехе."""
    client._client.request = AsyncMock(return_value=make_response(200, {"success": True}))

    ok = await client.unregister(event_id="evt-1", ticket_id="ticket-123")

    assert ok is True


@pytest.mark.asyncio
async def test_unregister_returns_false_if_no_key(client: EventsProviderClient) -> None:
    """unregister() возвращает False, если в ответе нет success."""
    client._client.request = AsyncMock(return_value=make_response(200, {}))

    ok = await client.unregister(event_id="evt-1", ticket_id="ticket-123")

    assert ok is False


@pytest.mark.asyncio
async def test_unregister_raises_on_404(client: EventsProviderClient) -> None:
    """unregister() выбрасывает ошибку при 404."""
    client._client.request = AsyncMock(return_value=make_response(404, {"detail": "not found"}))

    with pytest.raises(EventsProviderError):
        await client.unregister(event_id="evt-1", ticket_id="ticket-123")


@pytest.mark.asyncio
async def test_close_calls_aclose() -> None:
    """close() вызывает aclose() у httpx-клиента."""
    client = EventsProviderClient(base_url="http://test.local", api_key="k")
    client._client.aclose = AsyncMock()

    await client.close()

    client._client.aclose.assert_awaited_once()
