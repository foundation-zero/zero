FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:053efa9652f89ac056731b55b4912131fca1dd644d472b6a40340a62f183a5db AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy the project
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.15-slim-trixie@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY io_lists/ ./io_lists/
