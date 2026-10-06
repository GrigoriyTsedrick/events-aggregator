"""Исключения бизнес-логики."""


class ServiceError(Exception):
    """Базовая ошибка сервисов."""


class EventNotFoundError(ServiceError):
    """Событие не найдено в локальной БД."""


class EventNotPublishedError(ServiceError):
    """Событие не опубликовано, регистрация запрещена."""


class TicketNotFoundError(ServiceError):
    """Билет не найден."""


class SeatNotAvailableError(ServiceError):
    """Место занято или не существует."""
