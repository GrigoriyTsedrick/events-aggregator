FROM python:3.12-slim

# Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Создаём пользователя appuser (LMS запрещает запуск от root)
RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

WORKDIR /app

# Копируем зависимости
COPY --chown=appuser:appuser pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project

# Копируем весь код
COPY --chown=appuser:appuser . .

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
