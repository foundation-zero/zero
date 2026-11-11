FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:1017e944d8b320412287a572b8221cda45742348d0feb99e500f1f4c4b019206 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY packages/py/zero-health/ /app/packages/py/zero-health/
COPY packages/py/zero-modbus-bridge/ /app/packages/py/zero-modbus-bridge/
COPY packages/py/zero-mqtt/ /app/packages/py/zero-mqtt/
COPY zero-power-tags/pyproject.toml zero-power-tags/uv.lock zero-power-tags/README.md ./zero-power-tags/
COPY zero-power-tags/src ./zero-power-tags/src

WORKDIR /app/zero-power-tags/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim-trixie@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS runtime

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
