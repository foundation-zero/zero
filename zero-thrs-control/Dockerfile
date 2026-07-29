FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.13-slim-trixie AS prod-base

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
