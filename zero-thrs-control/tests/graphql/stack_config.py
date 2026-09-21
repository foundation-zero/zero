"""Where the two APIs under test are, and which MQTT topic prefixes each
reads.

thrs-api runs with the environment ``docker-compose.yml`` gives it. zero-mqtt-graphql
serves the specs ``scripts/aggregate-specs.sh`` generates (``DEFAULT_CONFIG``'s
prefixes) and, with ``PREFIX_STRATEGY=runtime``, rewrites them to the
``RUNTIME_*_PREFIX`` values of its own compose environment. The cross-API suites
seed each service on its own prefixes so both see the same state.
"""

import os
import re
from pathlib import Path

import yaml

from thrs.orchestration.config import Config
from thrs.spec.asyncapi import DEFAULT_CONFIG

REPO_ROOT = Path(__file__).resolve().parents[3]

# The services the suites talk to, as `docker compose` names them.
STACK_SERVICES = ("vernemq", "postgres", "thrs-api", "mqtt-graphql")

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


def thrs_api_config() -> Config:
    environment = _service_environment("thrs-api")
    return Config(
        _env_file=None,
        **{
            key.lower(): value
            for key, value in environment.items()
            if key.lower() in Config.model_fields
        },
    )


def mqtt_graphql_config() -> Config:
    environment = _service_environment("mqtt-graphql")
    if environment.get("PREFIX_STRATEGY") != "runtime":
        return DEFAULT_CONFIG
    return DEFAULT_CONFIG.model_copy(
        update={
            f"mqtt_{kind}_topic_prefix": environment[f"RUNTIME_{kind.upper()}_PREFIX"]
            for kind in ("devices", "controller", "simulator")
            if f"RUNTIME_{kind.upper()}_PREFIX" in environment
        }
    )
