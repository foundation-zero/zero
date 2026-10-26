FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim@sha256:331fbb158258608b9391e802305a9a2c9e42d689435c1d98706647122a122ab0 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

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

FROM python:3.13-slim-trixie@sha256:d98cc29d3266e535dd9da1099688d9cb3ca4753813571e071763d17725460962 AS prod-base

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

COPY --chown=1001:1001 --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

FROM prod-base AS fmu_compile

RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg build-essential && \
    rm -rf /var/lib/apt/lists/*


FROM prod-base AS control
USER 1001
ENTRYPOINT [ "python", "-m", "thrs.cli"]

FROM prod-base AS api
USER 1001
CMD ["uvicorn", "thrs.graphql.asgi:app", "--port", "5102", "--host", "0.0.0.0"]
