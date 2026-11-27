FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:3ee10471b12b57f6f86d03f68c44fbd4bb8d5540efa25ab3b89159e1216b1a70 AS builder
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

FROM python:3.15-slim-trixie@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5 AS runtime

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
