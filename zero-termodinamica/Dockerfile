FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:86a05dd8f19b21368fbb160c7e2ad0576780bebbe89114b6deeba2506f7612e1 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY zero-modbus-bridge/ /app/zero-modbus-bridge/
COPY zero-termodinamica/pyproject.toml zero-termodinamica/uv.lock zero-termodinamica/README.md ./zero-termodinamica/
COPY zero-termodinamica/src ./zero-termodinamica/src

WORKDIR /app/zero-termodinamica

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim-trixie@sha256:533b0b2f9b5d46fd097091cf826f27902f1d6c3bca714b6dc74551356aa97a51 AS runtime

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
