FROM python:3.13-slim-bookworm AS builder

ENV POETRY_VERSION=2.2.1 \
  POETRY_HOME=/opt/poetry \
  POETRY_CACHE_DIR=/opt/.cache \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY zero-prop-test/pyproject.toml zero-prop-test/poetry.lock ./zero-prop-test/

WORKDIR /app/zero-prop-test/

ENV POETRY_DYNAMIC_VERSIONING_COMMANDS=""

RUN poetry install --no-root

FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/zero-prop-test/.venv
ENV PATH="/app/zero-prop-test/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY zero-prop-test/src/ ./zero-prop-test

WORKDIR /app/zero-prop-test

ENTRYPOINT ["python", "-m", "zero_prop_test"]
CMD ["twincat"]
