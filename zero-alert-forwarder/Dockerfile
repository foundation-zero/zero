FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim@sha256:531f855bda2c73cd6ef67d56b733b357cea384185b3022bd09f05e002cd144ca AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY zero-alert-forwarder/pyproject.toml zero-alert-forwarder/uv.lock zero-alert-forwarder/README.md ./zero-alert-forwarder/
COPY zero-alert-forwarder/zero_alert_forwarder ./zero-alert-forwarder/zero_alert_forwarder

WORKDIR /app/zero-alert-forwarder

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.15-slim-bookworm@sha256:575f8bc12ec26542e0678bc6b60e385218248019d433157ec327264a78c3a853 AS runtime

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
