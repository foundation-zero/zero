FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:60a1cfdc8945ea9d12c8fe6221bfa256b2d94df43a93cc957a503346de9ca53b AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY zero-alert-forwarder/pyproject.toml zero-alert-forwarder/uv.lock zero-alert-forwarder/README.md ./zero-alert-forwarder/
COPY zero-alert-forwarder/zero_alert_forwarder ./zero-alert-forwarder/zero_alert_forwarder

WORKDIR /app/zero-alert-forwarder

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim-trixie@sha256:94d3426f1def7db4a106a232ac121bfd975393e5dfd40a619b955fae45fe7913 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/zero-alert-forwarder/.venv
ENV PATH="/app/zero-alert-forwarder/.venv/bin:$PATH"

RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

COPY --chown=1001:1001 --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app/zero-alert-forwarder

USER 1001

ENTRYPOINT ["python", "-m", "zero_alert_forwarder"]
