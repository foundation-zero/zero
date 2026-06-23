FROM python:3.13-slim-bookworm AS builder

ENV POETRY_VERSION=2.2.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_CACHE_DIR=/opt/.cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-root

FROM python:3.13-slim-bookworm AS prod-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd -g 1001 app && \
    useradd -r -u 1001 -g app app

COPY --chown=1001:1001 --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY --chown=1001:1001 ./src/thrs/ thrs/

FROM prod-base AS simulation

RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN fmpy compile /app/thrs/simulation/models/Thruster_Module_V19.fmu

USER 1001
CMD ["python", "-m", "thrs.cli", "run", "thrusters"]

FROM prod-base AS control
USER 1001
CMD ["uvicorn", "thrs.graphql.asgi:app", "--port", "5102", "--host", "0.0.0.0"]
