FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:1017e944d8b320412287a572b8221cda45742348d0feb99e500f1f4c4b019206 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app/zero-atpx-nmea

COPY packages/py/zero-health/ /app/packages/py/zero-health/
COPY packages/py/zero-mqtt/ /app/packages/py/zero-mqtt/

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=zero-atpx-nmea/uv.lock,target=uv.lock \
    --mount=type=bind,source=zero-atpx-nmea/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev --no-editable

# Copy the project
COPY zero-atpx-nmea/pyproject.toml zero-atpx-nmea/uv.lock zero-atpx-nmea/README.md ./
COPY zero-atpx-nmea/src ./src

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim-trixie@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/zero-atpx-nmea/.venv
ENV PATH="/app/zero-atpx-nmea/.venv/bin:$PATH"

RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

COPY --from=builder --chown=1001:1001 ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY --chown=1001:1001 zero-atpx-nmea/src/ /app/zero-atpx-nmea/src/

WORKDIR /app/zero-atpx-nmea

USER 1001

ENTRYPOINT ["python", "-m", "zero_atpx_nmea"]
