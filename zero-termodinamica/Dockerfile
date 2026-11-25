FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:3ee10471b12b57f6f86d03f68c44fbd4bb8d5540efa25ab3b89159e1216b1a70 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY zero-termodinamica/pyproject.toml zero-termodinamica/uv.lock zero-termodinamica/README.md ./zero-termodinamica/
COPY zero-termodinamica/src ./zero-termodinamica/src

WORKDIR /app/zero-termodinamica

# pyproject.toml points at ../packages/py, which is /app/packages/py from the app directory.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=packages/py,target=/app/packages/py \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim-trixie@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/zero-termodinamica/.venv
ENV PATH="/app/zero-termodinamica/.venv/bin:$PATH"

RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

COPY --chown=1001:1001 --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY --chown=1001:1001 zero-termodinamica/src/ /app/zero-termodinamica/src/
COPY --chown=1001:1001 zero-termodinamica/modbus_bridges.json /app/zero-termodinamica/

WORKDIR /app/zero-termodinamica

USER 1001

ENTRYPOINT ["python", "-m", "zero_termodinamica"]
