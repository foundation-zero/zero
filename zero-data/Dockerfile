FROM python:3.13-slim-bookworm AS builder

RUN pip install poetry==2.0.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --without=test,dev,dbt

FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app

COPY io_lists /io_lists

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src/ ./

ENTRYPOINT ["python", "-m", "io_processing.main"]
