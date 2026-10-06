"""Клиент для работы с внешним Events Provider API."""
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class EventsProviderError(Exception):
    """Базовая ошибка при работе с Events Provider API."""


class EventsProviderClient:
    """Асинхронный клиент Events Provider API.

    Инкапсулирует все HTTP-запросы к внешнему сервису.
    Все URL заканчиваются на `/` — так требует API (иначе 301 redirect).
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"x-api-key": api_key},
            timeout=timeout,
            verify=False,  # dev-кластер с самоподписанным сертификатом
            follow_redirects=True,
        )

    async def __aenter__(self) -> "EventsProviderClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Закрыть HTTP-клиент. Вызывать при остановке приложения."""
        await self._client.aclose()

    async def events(
        self,
        changed_at: str,
        cursor: str | None = None,
    ) -> dict:
        """Получить одну страницу событий.

        Args:
            changed_at: дата в формате YYYY-MM-DD.
            cursor: опциональный курсор для следующей страницы.

        Returns:
            Словарь с полями next, previous, results.
        """
        params: dict[str, str] = {"changed_at": changed_at}
        if cursor:
            params["cursor"] = cursor

        logger.info("Запрос событий: changed_at=%s, cursor=%s", changed_at, cursor)

        response = await self._client.get("/api/events/", params=params)
        self._raise_for_status(response)
        return response.json()

    async def events_by_url(self, url: str) -> dict:
        """Получить страницу событий по полному URL (из поля next)."""
        logger.info("Запрос событий по URL: %s", url)
        response = await self._client.get(url)
        self._raise_for_status(response)
        return response.json()

    async def seats(self, event_id: str) -> list[str]:
        """Получить список свободных мест для события."""
        logger.info("Запрос мест для события: %s", event_id)
        response = await self._client.get(f"/api/events/{event_id}/seats/")
        self._raise_for_status(response)
        return response.json().get("seats", [])

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        seat: str,
        email: str,
    ) -> str:
        """Зарегистрировать участника на событие.

        Returns:
            ticket_id — идентификатор билета.
        """
        logger.info("Регистрация на событие %s, место %s", event_id, seat)
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "seat": seat,
            "email": email,
        }
        response = await self._client.post(
            f"/api/events/{event_id}/register/",
            json=payload,
        )
        self._raise_for_status(response)
        return response.json()["ticket_id"]

    async def unregister(self, event_id: str, ticket_id: str) -> bool:
        """Отменить регистрацию по ticket_id.

        Returns:
            True, если отмена прошла успешно.
        """
        logger.info("Отмена регистрации на событие %s, ticket %s", event_id, ticket_id)
        response = await self._client.request(
            "DELETE",
            f"/api/events/{event_id}/unregister/",
            json={"ticket_id": ticket_id},
        )
        self._raise_for_status(response)
        return response.json().get("success", False)

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Проверить статус ответа и бросить понятную ошибку."""
        if response.status_code >= 400:
            logger.error(
                "Ошибка Events Provider API: %s %s — %s",
                response.status_code,
                response.url,
                response.text[:200],
            )
            raise EventsProviderError(
                f"Events Provider API вернул {response.status_code}: {response.text[:200]}"
            )
