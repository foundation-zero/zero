FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim@sha256:331fbb158258608b9391e802305a9a2c9e42d689435c1d98706647122a122ab0 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY zero-modbus-bridge/ /app/zero-modbus-bridge/
COPY zero-hull-temperature/pyproject.toml zero-hull-temperature/uv.lock zero-hull-temperature/README.md ./zero-hull-temperature/
COPY zero-hull-temperature/zero_hull_temperature ./zero-hull-temperature/zero_hull_temperature

WORKDIR /app/zero-hull-temperature

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.13-slim-trixie@sha256:d98cc29d3266e535dd9da1099688d9cb3ca4753813571e071763d17725460962 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/zero-hull-temperature/.venv
ENV PATH="/app/zero-hull-temperature/.venv/bin:$PATH"

RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

COPY --chown=1001:1001 --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app/zero-hull-temperature

USER 1001

ENTRYPOINT ["python", "-m", "zero_hull_temperature"]
