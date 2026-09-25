"""Where the two APIs under test are, and which MQTT topic prefixes each
reads.

Both run with the environment ``docker-compose.yml`` gives them: thrs-api
builds its topics from ``MQTT_*_TOPIC_PREFIX``/``_SUFFIX``, zero-mqtt-graphql
fills the same variables into the ``x-env`` parameters of the specs
``scripts/aggregate-specs.sh`` generates. The cross-API suites seed each
service on its own topics so both see the same state.
"""

import os
import re
from pathlib import Path

import yaml

from thrs.orchestration.config import Config
from thrs.spec.asyncapi import TOPIC_SETTINGS

REPO_ROOT = Path(__file__).resolve().parents[3]

MQTT_HOST = "localhost"
MQTT_PORT = 1883

THRS_API = "thrs-api"
MQTT_GRAPHQL = "mqtt-graphql"
APIS = (THRS_API, MQTT_GRAPHQL)
URLS = {
    THRS_API: "http://localhost:5102/graphql",
    MQTT_GRAPHQL: "http://localhost:5103/graphql",
}
THRS_API_URL = URLS[THRS_API]
MQTT_GRAPHQL_URL = URLS[MQTT_GRAPHQL]

# Infrastructure both APIs sit on; always required.
_INFRA_SERVICES = ("vernemq", "postgres")
# Each API's own `docker compose` service (only these carry an HTTP endpoint the
# suites hit); infra is shared.
_API_SERVICE = {THRS_API: "thrs-api", MQTT_GRAPHQL: "mqtt-graphql"}

_APIS_ENV = "MIGRATION_APIS"


def selected_apis() -> tuple[str, ...]:
    """The APIs to exercise, honouring ``MIGRATION_APIS`` (default: both, in
    the canonical order). Raises on an unknown name so a typo fails loudly
    rather than silently skipping an API."""
    raw = os.environ.get(_APIS_ENV)
    if not raw:
        return APIS
    chosen = [name.strip() for name in raw.split(",") if name.strip()]
    unknown = [name for name in chosen if name not in APIS]
    if unknown:
        raise ValueError(
            f"{_APIS_ENV}={raw!r}: unknown API(s) {unknown}; known: {list(APIS)}"
        )
    # Preserve the canonical order regardless of how they were listed.
    return tuple(api for api in APIS if api in chosen)


def waited_services() -> tuple[str, ...]:
    """The `docker compose` services the stack fixture must bring up for the
    selected APIs: shared infra plus each selected API's own service. A solo
    ``mqtt-graphql`` run does not require thrs-api to be up."""
    return _INFRA_SERVICES + tuple(_API_SERVICE[api] for api in selected_apis())


# The services the suites talk to, as `docker compose` names them. Kept for
# callers that want the full set regardless of selection.
STACK_SERVICES = _INFRA_SERVICES + tuple(_API_SERVICE[api] for api in APIS)


def _interpolate(value: str) -> str:
    """docker-compose's ``${VAR}`` / ``${VAR:-default}`` substitution."""
    return re.sub(
        r"\$\{(\w+)(?::-([^}]*))?\}",
        lambda m: os.environ.get(m.group(1), m.group(2) or ""),
        value,
    )


def _service_environment(service: str) -> dict[str, str]:
    services = yaml.safe_load((REPO_ROOT / "docker-compose.yml").read_text())[
        "services"
    ]
    return {
        key: _interpolate(str(value))
        for key, value in services[service]["environment"].items()
    }


def _config_of(service: str) -> Config:
    """The ``Config`` a service reads from its compose environment."""
    environment = _service_environment(service)
    return Config.model_validate(
        {
            key.lower(): value
            for key, value in environment.items()
            if key.lower() in Config.model_fields
        }
    )


def thrs_api_config() -> Config:
    return _config_of("thrs-api")


def mqtt_graphql_config() -> Config:
    """zero-mqtt-graphql's topic settings; like the bridge, a missing one fails."""
    environment = _service_environment("mqtt-graphql")
    missing = [n.upper() for n in TOPIC_SETTINGS if n.upper() not in environment]
    if missing:
        raise KeyError(f"mqtt-graphql's compose environment lacks {missing}")
    return _config_of("mqtt-graphql")
