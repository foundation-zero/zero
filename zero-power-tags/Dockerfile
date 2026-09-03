FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY zero-modbus-bridge/ /app/zero-modbus-bridge/
COPY zero-power-tags/pyproject.toml zero-power-tags/uv.lock zero-power-tags/README.md ./zero-power-tags/
COPY zero-power-tags/src ./zero-power-tags/src

WORKDIR /app/zero-power-tags/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/zero-power-tags/.venv
ENV PATH="/app/zero-power-tags/.venv/bin:$PATH"

RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

COPY --from=builder --chown=1001:1001 ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY --chown=1001:1001 zero-power-tags/src/ /app/zero-power-tags/src/
COPY --chown=1001:1001 zero-power-tags/modbus_bridges.json /app/zero-power-tags/

ENV MODBUS_BRIDGES_PATH=/app/zero-power-tags/modbus_bridges.json

WORKDIR /app/zero-power-tags

USER 1001

ENTRYPOINT ["python", "-m", "zero_power_tags"]
CMD ["run"]
