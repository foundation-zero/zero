FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim@sha256:3ee10471b12b57f6f86d03f68c44fbd4bb8d5540efa25ab3b89159e1216b1a70 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app/zero-loads-app

# Install dependencies
# pyproject.toml points at ../packages/py, which is /app/packages/py from the app directory.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=packages/py,target=/app/packages/py \
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
    --mount=type=bind,source=packages/py,target=/app/packages/py \
    uv sync --locked --no-editable

FROM python:3.15-slim-trixie@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5 AS runtime

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
