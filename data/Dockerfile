FROM python:3.13-slim-bookworm AS builder

ENV POETRY_VERSION=2.0.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_CACHE_DIR=/opt/.cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    # Nice to have optimizations
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY ./config.py ./config.py

COPY ./postgres ./postgres
COPY ./setup_postgres.py ./setup_postgres.py

COPY ./risingwave ./risingwave
COPY ./setup_risingwave.py ./setup_risingwave.py

# CMD ["tail", "-f", "/dev/null"]
ENTRYPOINT ["python", "-m"]
