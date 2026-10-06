"""Бизнес-логика синхронизации событий с Events Provider API."""
import logging
from datetime import datetime, timezone

from src.client.events_provider import EventsProviderClient
from src.client.paginator import EventsPaginator
from src.repositories.event import EventRepository
from src.repositories.place import PlaceRepository
from src.repositories.sync import SyncRepository

logger = logging.getLogger(__name__)

FIRST_SYNC_DATE = "2000-01-01"


class SyncService:
    """Сервис синхронизации событий с внешним API."""

    def __init__(
        self,
        client: EventsProviderClient,
        events: EventRepository,
        places: PlaceRepository,
        sync_meta: SyncRepository,
    ) -> None:
        self._client = client
        self._events = events
        self._places = places
        self._sync_meta = sync_meta

    async def sync(self) -> dict:
        """Выполнить синхронизацию.

        Returns:
            Словарь со статистикой: processed, errors, changed_at.
        """
        meta = await self._sync_meta.get_singleton()

        # Определяем, с какой даты забирать изменения
        if meta.last_changed_at is None:
            changed_at = FIRST_SYNC_DATE
            logger.info("Первая синхронизация — забираем все события")
        else:
            # Берём дату, а не полный datetime — API принимает YYYY-MM-DD
            changed_at = meta.last_changed_at.strftime("%Y-%m-%d")
            logger.info("Инкрементальная синхронизация с %s", changed_at)

        meta.sync_status = "running"
        await self._sync_meta.update(meta, sync_status="running")

        processed = 0
        errors = 0
        max_changed_at: datetime | None = None

        try:
            async for event in EventsPaginator(self._client, changed_at=changed_at):
                try:
                    await self._save_event(event)
                    processed += 1

                    # Парсим changed_at события
                    ev_changed_at = self._parse_datetime(event.get("changed_at"))
                    if ev_changed_at and (max_changed_at is None or ev_changed_at > max_changed_at):
                        max_changed_at = ev_changed_at
                except Exception as exc:  # noqa: BLE001 — ловим всё, чтобы не падать
                    errors += 1
                    logger.exception("Ошибка сохранения события %s: %s", event.get("id"), exc)

            # Обновляем метаданные
            now = datetime.now(timezone.utc)
            await self._sync_meta.update(
                meta,
                last_sync_time=now,
                last_changed_at=max_changed_at or meta.last_changed_at,
                sync_status="success" if errors == 0 else "partial",
            )
            logger.info(
                "Синхронизация завершена: обработано=%d, ошибок=%d",
                processed,
                errors,
            )
        except Exception as exc:
            await self._sync_meta.update(meta, sync_status="failed")
            logger.exception("Синхронизация упала: %s", exc)
            raise

        return {
            "processed": processed,
            "errors": errors,
            "changed_at": changed_at,
        }

    async def _save_event(self, event: dict) -> None:
        """Сохранить площадку и событие в БД (upsert)."""
        place_data = event["place"]
        await self._places.upsert(
            {
                "id": place_data["id"],
                "name": place_data["name"],
                "city": place_data["city"],
                "address": place_data["address"],
                "seats_pattern": place_data["seats_pattern"],
                "changed_at": self._parse_datetime(place_data["changed_at"]),
                "created_at": self._parse_datetime(place_data["created_at"]),
            }
        )

        await self._events.upsert(
            {
                "id": event["id"],
                "name": event["name"],
                "place_id": place_data["id"],
                "event_time": self._parse_datetime(event["event_time"]),
                "registration_deadline": self._parse_datetime(event["registration_deadline"]),
                "status": event["status"],
                "number_of_visitors": event["number_of_visitors"],
                "changed_at": self._parse_datetime(event["changed_at"]),
                "created_at": self._parse_datetime(event["created_at"]),
                "status_changed_at": self._parse_datetime(event["status_changed_at"]),
            }
        )

    def _parse_datetime(self, value: str | None) -> datetime | None:
        """Распарсить ISO 8601 дату из ответа API."""
        if value is None:
            return None
        return datetime.fromisoformat(value)
