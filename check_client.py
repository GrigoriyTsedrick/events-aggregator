"""Временный скрипт для проверки клиента."""
import asyncio

from src.client.events_provider import EventsProviderClient
from src.client.paginator import EventsPaginator
from src.core.config import settings


async def main() -> None:
    async with EventsProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.events_provider_api_key,
    ) as client:
        count = 0
        async for event in EventsPaginator(client, changed_at="2000-01-01"):
            count += 1
            if count <= 3:
                print(f"- {event['name']} ({event['place']['city']})")

        print(f"\nВсего событий: {count}")


if __name__ == "__main__":
    asyncio.run(main())
