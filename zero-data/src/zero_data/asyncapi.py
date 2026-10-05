"""The AsyncAPI 3.0 document of the MarPower (AMCS) topics, built from the IO list."""

import logging
import re
from collections import defaultdict
from typing import Any

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


def stamped_schema_name(data_type: str) -> str:
    return f"Stamped_{data_type.lower()}"


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


def address(topic: str) -> str:
    root, _, rest = topic.partition("/")
    if root != TOPIC_ROOT:
        raise ValueError(f"Topic {topic!r} is not under {TOPIC_ROOT!r}")
    return f"{TOPIC_ROOT}/{rest}"


def key(topic: str) -> str:
    return topic.replace("/", ".")


def graphql_words(name: str) -> tuple[str, ...]:
    """Keys the bridge serves under the same GraphQL field name share these words."""
    return tuple(word.lower() for word in re.split(r"[^0-9A-Za-z]+", name) if word)


def served_fields(topic: IOTopic) -> list[IOValue]:
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
    return sorted(
        (fields[0] for fields in by_words.values() if len(fields) == 1),
        key=lambda field: field.name,
    )


def channel(topic: IOTopic, fields: list[IOValue]) -> dict[str, Any]:
    return {
        "address": address(topic.topic),
        "messages": {
            "message": {
                "payload": {
                    "type": "object",
                    "properties": {
                        field.name: {
                            "$ref": SCHEMA_REF_PREFIX
                            + stamped_schema_name(field.data_type)
                        }
                        for field in fields
                    },
                },
                "x-ttl": CHANNEL_TTL,
            }
        },
    }


def build_asyncapi(io_result: IOResult) -> dict[str, Any]:
    topics = sorted(io_result.topics, key=lambda topic: topic.topic)
    fields = {topic.topic: served_fields(topic) for topic in topics}
    data_types = sorted(
        {field.data_type for served in fields.values() for field in served}
    )
    return {
        "asyncapi": "3.0.0",
        "info": {"title": "MarPower AMCS", "version": "1.0.0"},
        "defaultContentType": "application/json",
        "channels": {
            key(topic.topic): channel(topic, fields[topic.topic]) for topic in topics
        },
        "operations": {
            key(topic.topic): {
                "action": "send",
                "channel": {"$ref": f"#/channels/{key(topic.topic)}"},
            }
            for topic in topics
        },
        "components": {
            "schemas": {
                stamped_schema_name(data_type): stamped_schema(data_type)
                for data_type in data_types
            }
        },
    }
