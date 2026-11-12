"""The AsyncAPI 3.0 document of the MarPower (AMCS) topics, built from the IO list."""

import logging
import re
from collections import defaultdict
from enum import IntEnum
from typing import Any

import stringcase  # type: ignore

from zero_data.io_list.enums import ENUMS
from zero_data.io_list.extra_topics import EXTRA_TOPICS
from zero_data.io_list.managed_topics import (
    SYSTEMS,
    ManagedTopic,
    extract_managed_topics,
)
from zero_data.io_list.types import IOResult, IOTopic, IOValue

logger = logging.getLogger(__name__)

# The IO list names every topic under this segment; the document keeps it as
# an address parameter, filled in from the environment variable of the same
# name as THRS does (production: marpower, simulation: simulation).
TOPIC_ROOT = "marpower"
ENV_KEY = "x-env"

CHANNEL_TTL = "1h"

JSON_TYPES = {
    "REAL": "number",
    "BOOLEAN": "boolean",
    "INTEGER": "integer",
    "BIGINT": "integer",
    "STRING": "string",
    "TIMESTAMP": "string",
}

SCHEMA_REF_PREFIX = "#/components/schemas/"


def value_type(field: str, data_type: str) -> str:
    """What a field's value is: its enum when it has one, else its JSON type."""
    enum = ENUMS.get(field)
    return enum.__name__ if enum else JSON_TYPES[data_type]


def stamped_schema_name(value_type: str) -> str:
    return f"stamped{stringcase.capitalcase(value_type)}"


def stamped_schema(value_type: str, value: dict[str, Any]) -> dict[str, Any]:
    """Every AMCS value is published as {"Value": 1.0, "TimeStamp": "timestamp", ...}."""
    return {
        "title": stamped_schema_name(value_type),
        "type": "object",
        "properties": {
            "Value": value,
            "TimeStamp": {"type": "string", "format": "date-time"},
        },
        "required": ["Value", "TimeStamp"],
    }


def enum_schema(enum: type[IntEnum]) -> dict[str, Any]:
    """An integer enum whose values are named, as named constants."""
    return {
        "title": enum.__name__,
        "type": "integer",
        "oneOf": [{"const": member.value, "title": member.name} for member in enum],
    }


def component_name(component: str) -> str:
    return stringcase.pascalcase(component)


def component_schema(name: str, fields: dict[str, str]) -> dict[str, Any]:
    return {
        "title": stringcase.titlecase(name),
        "type": "object",
        "properties": {
            field: {
                "$ref": SCHEMA_REF_PREFIX
                + stamped_schema_name(value_type(field, data_type))
            }
            for field, data_type in fields.items()
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


def _merge_component_fields(
    existing: dict[str, Any] | None, fields: dict[str, Any], topic: ManagedTopic
) -> dict[str, Any]:
    """Merge incoming fields with existing fields, warning on conflict."""
    if existing is None or existing.items() <= fields.items():
        return fields

    if fields.items() <= existing.items():
        return existing

    logger.warning(
        "We found mismatching types for component '%s' on topic '%s', ignoring.",
        topic.component,
        topic.topic.topic,
    )
    return existing


def extract_schemas(
    topics: list[ManagedTopic],
) -> dict[str, dict[str, Any]]:
    component_types: dict[str, dict[str, Any]] = {}
    for topic in topics:
        component_types[topic.component] = _merge_component_fields(
            component_types.get(topic.component),
            served_fields(topic.topic),
            topic,
        )

    all_fields = [
        (field, data_type)
        for fields in component_types.values()
        for field, data_type in fields.items()
    ]
    enums = sorted(
        {enum for field, _ in all_fields if (enum := ENUMS.get(field))},
        key=lambda enum: enum.__name__,
    )
    values = {
        json_type: {"type": json_type}
        for json_type in sorted({JSON_TYPES[data_type] for _, data_type in all_fields})
    } | {enum.__name__: {"$ref": SCHEMA_REF_PREFIX + enum.__name__} for enum in enums}

    return (
        {
            component_name(component): component_schema(component, fields)
            for component, fields in component_types.items()
        }
        | {enum.__name__: enum_schema(enum) for enum in enums}
        | {
            stamped_schema_name(name): stamped_schema(name, value)
            for name, value in values.items()
        }
    )


def channel(topic: ManagedTopic) -> dict[str, Any]:
    return {
        "address": address(topic.topic.topic),
        "x-zero-yard-tag": topic.topic.yard_tag.replace("_", "-")
        if topic.topic.yard_tag
        else None,
        "x-zero-component-type": topic.component,
        **({"x-zero-valve-type": topic.valve_type} if topic.valve_type else {}),
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

    topics = sorted(managed_topics + EXTRA_TOPICS, key=lambda topic: topic.topic.topic)

    subscribe_channels = {
        f"subscribe{system}": {
            "address": f"marpower/{system}/#",
            "messages": {},
        }
        for system in SYSTEMS
    }
    channels = {key(topic): channel(topic) for topic in topics}

    subscribe_operations = {
        f"subscribe{system}": {
            "action": "send",
            "channel": {"$ref": f"#/channels/subscribe{system}"},
        }
        for system in SYSTEMS
    }
    operations = {
        key(topic): {
            "action": "send",
            "channel": {"$ref": f"#/channels/{key(topic)}"},
        }
        for topic in topics
    }

    schemas = extract_schemas(topics)

    return {
        "asyncapi": "3.0.0",
        "info": {"title": "MarPower AMCS", "version": "1.0.0"},
        "defaultContentType": "application/json",
        "channels": subscribe_channels | channels,
        "operations": subscribe_operations | operations,
        "components": {"schemas": schemas},
    }
