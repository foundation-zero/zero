FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:1017e944d8b320412287a572b8221cda45742348d0feb99e500f1f4c4b019206 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY zero-alert-forwarder/pyproject.toml zero-alert-forwarder/uv.lock zero-alert-forwarder/README.md ./zero-alert-forwarder/
COPY zero-alert-forwarder/zero_alert_forwarder ./zero-alert-forwarder/zero_alert_forwarder

WORKDIR /app/zero-alert-forwarder

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim-trixie@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS runtime

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
