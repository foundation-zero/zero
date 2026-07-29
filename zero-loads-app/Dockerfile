FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
COPY zero-loads-app/pyproject.toml zero-loads-app/uv.lock zero-loads-app/README.md ./zero-loads-app/
COPY zero-loads-app/src ./zero-loads-app/src
COPY zero-generator zero-generator/

RUN --mount=type=cache,target=/root/.cache/uv \
    cd zero-loads-app && uv sync --locked --no-editable

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
