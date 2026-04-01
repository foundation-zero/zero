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

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY ./src/thrs/ thrs/

FROM prod-base AS simulation

RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg build-essential && \
    curl -fsSL http://build.openmodelica.org/apt/openmodelica.asc | \
    gpg --dearmor -o /usr/share/keyrings/openmodelica-keyring.gpg && \
    echo "deb [arch=arm64 signed-by=/usr/share/keyrings/openmodelica-keyring.gpg] \
    https://build.openmodelica.org/apt \
    bookworm \
    stable" | tee /etc/apt/sources.list.d/openmodelica.list && \
    rm -rf /var/lib/apt/lists/*

RUN fmpy compile /app/thrs/simulation/models/thruster_moduleV18.fmu
CMD ["python", "-m", "thrs.cli", "run", "thrusters"]

FROM prod-base AS control
CMD ["uvicorn", "thrs.graphql.strawberry:app", "--port", "5102", "--host", "0.0.0.0"]
