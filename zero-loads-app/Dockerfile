FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy dependency packages first (needed for resolution)
COPY zero-generator zero-generator/

WORKDIR /app/zero-loads-app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=zero-loads-app/uv.lock,target=uv.lock \
    --mount=type=bind,source=zero-loads-app/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

WORKDIR /app

# Copy the project
COPY zero-loads-app/pyproject.toml zero-loads-app/uv.lock zero-loads-app/README.md ./zero-loads-app/
COPY zero-loads-app/src ./zero-loads-app/src

WORKDIR /app/zero-loads-app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/zero-loads-app/.venv
ENV PATH="/app/zero-loads-app/.venv/bin:$PATH"

RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

COPY --from=builder --chown=1001:1001 ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app/zero-loads-app
USER 1001

ENTRYPOINT ["python", "-m", "loads"]
CMD ["api"]
