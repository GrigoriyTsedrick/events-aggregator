"""Настройки приложения через pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки сервиса, читаются из .env или переменных окружения."""

    app_title: str = "Events Aggregator"
    app_version: str = "0.1.0"

    # LMS подставит готовую строку подключения — используем её в приоритете
    postgres_connection_string: str | None = None

    # Fallback для локальной разработки
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "events_aggregator"
    postgres_host: str = "db"
    postgres_port: int = 5432

    events_provider_url: str
    events_provider_api_key: str

    sync_interval_hours: int = 24

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        """Строка подключения к PostgreSQL.

        В кластере LMS используем POSTGRES_CONNECTION_STRING.
        Локально — собираем URL из отдельных переменных.
        """
        if self.postgres_connection_string:
            url = self.postgres_connection_string
            # Приводим схему к asyncpg-совместимой
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
