FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim@sha256:331fbb158258608b9391e802305a9a2c9e42d689435c1d98706647122a122ab0 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app/zero-atpx-nmea

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

FROM python:3.13-slim-trixie@sha256:d98cc29d3266e535dd9da1099688d9cb3ca4753813571e071763d17725460962 AS runtime

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
