"""Where the two APIs under test get their MQTT topic prefixes from.

thrs-api runs with the environment ``docker-compose.yml`` gives it; zero-mqtt-graphql
serves the specs ``scripts/aggregate-specs.sh`` generates, which bake in
``DEFAULT_CONFIG``'s prefixes unless overridden. The cross-API suites publish to
both so both services see the same state.
"""

import os
import re
from pathlib import Path

import yaml

from thrs.orchestration.config import Config
from thrs.spec.asyncapi import DEFAULT_CONFIG

REPO_ROOT = Path(__file__).resolve().parents[3]


def _interpolate(value: str) -> str:
    """docker-compose's ``${VAR}`` / ``${VAR:-default}`` substitution."""
    return re.sub(
        r"\$\{(\w+)(?::-([^}]*))?\}",
        lambda m: os.environ.get(m.group(1), m.group(2) or ""),
        value,
    )


def thrs_api_config() -> Config:
    services = yaml.safe_load((REPO_ROOT / "docker-compose.yml").read_text())[
        "services"
    ]
    environment = services["thrs-api"]["environment"]
    return Config(
        _env_file=None,
        **{
            key.lower(): _interpolate(str(value))
            for key, value in environment.items()
            if key.lower() in Config.model_fields
        },
    )


def mqtt_graphql_config() -> Config:
    return DEFAULT_CONFIG
