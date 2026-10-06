"""The AsyncAPI 3.0 document of the MarPower (AMCS) topics, built from the IO list."""

import logging
import re
from collections import defaultdict
from typing import Any

import stringcase  # type: ignore

from zero_data.io_list.managed_topics import ManagedTopic, extract_managed_topics
from zero_data.io_list.types import IOResult, IOTopic, IOValue

logger = logging.getLogger(__name__)

# The IO list names every topic under this segment; the document keeps it as
# an address parameter, filled in from the environment variable of the same
# name as THRS does (production: marpower, simulation: simulation).
TOPIC_ROOT = "marpower"
ENV_KEY = "x-env"

# As in THRS, a served value never expires into null; TimeStamp shows its age.
CHANNEL_TTL = "unbounded"

JSON_TYPES = {
    "REAL": "number",
    "BOOLEAN": "boolean",
    "INTEGER": "integer",
    "BIGINT": "integer",
    "STRING": "string",
    "TIMESTAMP": "string",
}

SCHEMA_REF_PREFIX = "#/components/schemas/"

TOPICS_ALLOWLIST = (
    "marpower/150000",  # propulsion
    "marpower/210000",  # Bilge
    "marpower/250000",  # Freshwater
    "marpower/280000",  # Hydraulic sail
    "marpower/380000",  # Seawater
    "marpower/450000",  # DC distribution
    "marpower/500000",  # Thrs
    "marpower/550000",  # Navigation lights
)


def stamped_schema_name(data_type: str) -> str:
    return f"stamped{stringcase.capitalcase(JSON_TYPES[data_type])}"


def stamped_schema(data_type: str) -> dict[str, Any]:
    """Every AMCS value is published as {Value, TimeStamp, ...}."""
    return {
        "title": stamped_schema_name(data_type),
        "type": "object",
        "properties": {
            "Value": {"type": JSON_TYPES[data_type]},
            "TimeStamp": {"type": "string", "format": "date-time"},
        },
        "required": ["Value", "TimeStamp"],
    }


def component_name(component: str) -> str:
    return stringcase.pascalcase(component)


def component_schema(name: str, fields: dict[str, str]) -> dict[str, Any]:
    return {
        "title": stringcase.titlecase(name),
        "type": "object",
        "properties": {
            name: {"$ref": SCHEMA_REF_PREFIX + stamped_schema_name(data_type)}
            for name, data_type in fields.items()
        },
    }


def address(topic: str) -> str:
    root, _, rest = topic.partition("/")
    if root != TOPIC_ROOT:
        raise ValueError(f"Topic {topic!r} is not under {TOPIC_ROOT!r}")
    return f"{TOPIC_ROOT}/{rest}"


def key(topic: ManagedTopic) -> str:
    return f"{topic.system_name}.{topic.module_name}.{topic.technical_name}"


def graphql_words(name: str) -> tuple[str, ...]:
    """Keys the bridge serves under the same GraphQL field name share these words."""
    return tuple(word.lower() for word in re.split(r"[^0-9A-Za-z]+", name) if word)


def served_fields(topic: IOTopic) -> dict[str, str]:
    """The fields of a topic, without those whose GraphQL names collide.

    The bridge names a field after its key, so two keys that differ only in
    case or punctuation (e.g. Tank_Level_Sensor and Tank_level_sensor) would
    stop it; neither can be told apart, so both are left out.
    """
    # A key listed more than once (e.g. per yard tag) is one field on the wire.
    by_name = {field.name: field for field in topic.fields}
    by_words: dict[tuple[str, ...], list[IOValue]] = defaultdict(list)
    for field in by_name.values():
        by_words[graphql_words(field.name)].append(field)
    for fields in by_words.values():
        if len(fields) > 1:
            logger.warning(
                "Leaving out fields of %s whose GraphQL names collide: %s",
                topic.topic,
                ", ".join(sorted(field.name for field in fields)),
            )
    return {
        fields[0].name: fields[0].data_type
        for fields in by_words.values()
        if len(fields) == 1
    }


def extract_schemas(
    topics: list[ManagedTopic],
) -> dict[str, dict[str, Any]]:
    component_types = {}
    field_types: set[str] = set()

    for topic in topics:
        component = topic.component
        fields = served_fields(topic.topic)
        field_types.update(fields.values())

        if component not in component_types:
            component_types[component] = fields
            continue

        if component_types[component] == fields:
            continue

        combined = {**fields, **component_types[component]}

        if combined == component_types[component]:
            # Fields is a subset of what we already have
            continue

        if combined == fields:
            # What we already have is a subset of fields, so update to the bigger set
            component_types[component] = fields
            continue

        logger.warning(
            "We found mismatching types for component '%s' on topic '%s', ignoring.",
            component,
            topic.topic.topic,
        )

    return {
        **{
            component_name(component): component_schema(component, fields)
            for component, fields in component_types.items()
        },
        **{
            stamped_schema_name(data_type): stamped_schema(data_type)
            for data_type in sorted(field_types)
        },
    }


def channel(topic: ManagedTopic) -> dict[str, Any]:
    return {
        "address": address(topic.topic.topic),
        "x-zero-yard-tag": topic.topic.yard_tag,
        "x-zero-component-type": topic.component,
        "messages": {
            "message": {
                "payload": {
                    "$ref": f"{SCHEMA_REF_PREFIX}{component_name(topic.component)}"
                },
                "x-ttl": CHANNEL_TTL,
            }
        },
    }


def build_asyncapi(io_result: IOResult) -> dict[str, Any]:
    managed_topics, _, _ = extract_managed_topics(io_result.topics)

    topics = sorted(managed_topics, key=lambda topic: topic.topic.topic)

    channels = {key(topic): channel(topic) for topic in topics}
    operations = {
        key(topic): {
            "action": "receive",
            "channel": {"$ref": f"#/channels/{key(topic)}"},
        }
        for topic in topics
    }
    schemas = extract_schemas(topics)

    return {
        "asyncapi": "3.0.0",
        "info": {"title": "MarPower AMCS", "version": "1.0.0"},
        "defaultContentType": "application/json",
        "channels": channels,
        "operations": operations,
        "components": {"schemas": schemas},
    }
