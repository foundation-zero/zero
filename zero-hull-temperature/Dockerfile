FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:3ee10471b12b57f6f86d03f68c44fbd4bb8d5540efa25ab3b89159e1216b1a70 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY zero-hull-temperature/pyproject.toml zero-hull-temperature/uv.lock zero-hull-temperature/README.md ./zero-hull-temperature/
COPY zero-hull-temperature/zero_hull_temperature ./zero-hull-temperature/zero_hull_temperature

WORKDIR /app/zero-hull-temperature

# pyproject.toml points at ../packages/py, which is /app/packages/py from the app directory.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=packages/py,target=/app/packages/py \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim-trixie@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5 AS runtime

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
