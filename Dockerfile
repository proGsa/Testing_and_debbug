FROM python:3.13-slim AS builder

# Переменные окружения
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=2.1.1 \
    PATH="$POETRY_HOME/bin:$PATH" \
    PYTHONPATH=/app/src

# Рабочая директория
WORKDIR /app

# Установка системных зависимостей и Poetry
RUN apt-get update && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python - \
    && chmod +x /opt/poetry/bin/poetry

ENV PATH="/opt/poetry/bin:$PATH"

COPY pyproject.toml poetry.lock ./
# Установка зависимостей без виртуального окружения
RUN poetry config virtualenvs.create false \
&& poetry install --no-root --no-interaction --no-ansi
RUN pip install asyncpg && pip uninstall -y psycopg2-binary

RUN poetry add --group dev allure-pytest
RUN pip install psutil pytest-xdist
# Установка Allure
RUN apt-get update && apt-get install -y curl unzip \
&& curl -o allure-2.27.0.tgz -Ls https://github.com/allure-framework/allure2/releases/download/2.27.0/allure-2.27.0.tgz \
&& tar -zxvf allure-2.27.0.tgz -C /opt/ \
&& ln -s /opt/allure-2.27.0/bin/allure /usr/local/bin/allure \
&& rm allure-2.27.0.tgz

COPY . .
COPY ./analyze_processes.py .

# --- Финальный рантайм-образ ---
FROM python:3.13-slim

ENV PYTHONPATH=/app/src \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

# Копируем зависимости и бинарники
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /opt/allure-2.27.0 /opt/allure-2.27.0

# Копируем Poetry
COPY --from=builder /opt/poetry /opt/poetry


COPY . .

# Линтинг и типизация
RUN poetry run ruff check --fix ./src ./tests
RUN poetry run mypy ./src ./tests


CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
