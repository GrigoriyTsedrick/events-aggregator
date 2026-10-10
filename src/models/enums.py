"""Перечисления, используемые в моделях и сервисах."""
from enum import StrEnum


class EventStatus(StrEnum):
    """Статусы события.

    Внешний API возвращает эти значения в виде строк.
    Наследование от str позволяет сравнивать их с обычными строками:
    EventStatus.PUBLISHED == "published" → True
    """

    NEW = "new"
    PUBLISHED = "published"
    FINISHED = "finished"
