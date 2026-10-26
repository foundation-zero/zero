FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:86a05dd8f19b21368fbb160c7e2ad0576780bebbe89114b6deeba2506f7612e1 AS builder
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

FROM python:3.15-slim-trixie@sha256:533b0b2f9b5d46fd097091cf826f27902f1d6c3bca714b6dc74551356aa97a51 AS runtime

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
