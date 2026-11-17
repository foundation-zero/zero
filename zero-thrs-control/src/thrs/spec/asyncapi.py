"""The AsyncAPI 3.0 document of the THRS control system.

Channels are recorded from the runtime's own channel wiring, so the document cannot drift from it.
"""

from collections.abc import Mapping
from logging import warning
from typing import Any

from asyncapi3 import AsyncAPI3
from asyncapi3.models import (
    Channel,
    Channels,
    Components,
    Info,
    Message,
    Messages,
    Operation,
    Operations,
    Reference,
    Schema,
    Schemas,
    Server,
    Servers,
)
from pydantic.json_schema import (
    GenerateJsonSchema,
    JsonSchemaMode,
    JsonSchemaValue,
    models_json_schema,
)
from pydantic_core import core_schema

from thrs.input_output.base import ThrsValues
from thrs.orchestration.config import Config
from thrs.runtime.descriptions.simulation import MODES, Mode, lookup_mode
from thrs.spec.recording_connector import (
    TopicMapping,
    collect_topics,
    simulation_union_names,
)

# As in thrs-api, a served value never expires into null.
CHANNEL_TTL = "1h"


class _NamedEnumsJsonSchema(GenerateJsonSchema):
    """Writes each enum as named constants: a `oneOf` of `const` with `title`.

    This is the standard JSON Schema way to name enum values, in place of a
    bare `enum`. With it, the MQTT GraphQL bridge exposes an integer enum such
    as `PumpControlMode` as a GraphQL enum rather than a plain `Int`.
    """

    def enum_schema(self, schema: core_schema.EnumSchema) -> JsonSchemaValue:
        result = super().enum_schema(schema)
        values = result.pop("enum")
        result["oneOf"] = [
            {"const": value, "title": member.name}
            for value, member in zip(values, schema["members"], strict=True)
        ]
        return result


def _channel_key(topic: str) -> str:
    return topic.replace("/", "_")


def _operation_key(topic: TopicMapping) -> str:
    return topic.topic.replace("/", "_")


def _message_key(payload_type: type[ThrsValues]) -> str:
    return f"{payload_type.__module__.split('.')[-1]}{payload_type.__name__.replace('[', '').replace(']', '')}"


# The property that tells the classes of a union apart; every simulation payload names its mode
# in it (`simulation_type_field`).
UNION_DISCRIMINATOR = "SimulationType"


def _discriminated_union(
    payload_types: list[type[ThrsValues]],
    # As models_json_schema returns it: by (model, mode).
    schema_map: Mapping[Any, JsonSchemaValue],
    schemas: Mapping[str, JsonSchemaValue],
) -> JsonSchemaValue:
    """
    The schema of a topic that carries payloads of several classes: a `oneOf` of the classes with
    AsyncAPI's `discriminator`, which the union itself must declare and require.
    """
    arms = [
        schema_map[(payload_type, "serialization")] for payload_type in payload_types
    ]
    values = [
        schemas[arm["$ref"].split("/")[-1]]["properties"][UNION_DISCRIMINATOR]["const"]
        for arm in arms
    ]
    return {
        "type": "object",
        "discriminator": UNION_DISCRIMINATOR,
        "required": [UNION_DISCRIMINATOR],
        "properties": {UNION_DISCRIMINATOR: {"type": "string", "enum": values}},
        "oneOf": arms,
    }


def _build_asyncapi(
    title: str,
    version: str,
    mode: Mode,
    topics: list[TopicMapping],
    union_names: Mapping[str, str] | None = None,
) -> AsyncAPI3:
    """
    The document for the registered (template, direction) groups. A topic recorded with several
    payload classes gets one payload, the union `union_names` names for it.
    """

    payloads: list[tuple[type[ThrsValues], JsonSchemaMode]] = [
        (topic_data.payload_type, "serialization") for topic_data in topics
    ]
    schema_map, defs = models_json_schema(
        payloads,
        by_alias=True,
        ref_template="#/components/schemas/{model}",
        schema_generator=_NamedEnumsJsonSchema,
    )
    schemas = defs.get("$defs", {})

    channels: Mapping[str, Channel | Reference] = {}
    channels.update(
        {
            f"thrs_controller_{module}": Channel(
                address=f"thrs/controller/{module}/#",
                **{"x-ttl": CHANNEL_TTL},  # type: ignore
            )
            for module in mode.control_modules
        }
    )

    operations: Mapping[str, Operation | Reference] = {}
    operations.update(
        {
            f"subscribe_{module}": Operation(
                action="send",
                channel=Reference(**{"$ref": f"#/channels/thrs_controller_{module}"}),
            )
            for module in mode.control_modules
        }
    )

    payload_types: dict[str, list[type[ThrsValues]]] = {}
    first_topics: dict[str, TopicMapping] = {}
    for topic_data in topics:
        first_topics.setdefault(topic_data.topic, topic_data)
        types = payload_types.setdefault(topic_data.topic, [])
        if topic_data.payload_type not in types:
            types.append(topic_data.payload_type)

    messages: Mapping[str, Message | Reference] = {}
    for topic_data in sorted(first_topics.values(), key=lambda topic: topic.topic):
        types = payload_types[topic_data.topic]
        json_schema: JsonSchemaValue
        if len(types) == 1:
            message_key = _message_key(topic_data.payload_type)
            json_schema = schema_map[(topic_data.payload_type, "serialization")]
        else:
            message_key = (union_names or {}).get(topic_data.topic, "")
            if not message_key:
                raise ValueError(
                    f"{topic_data.topic} carries {len(types)} payload classes, but no union "
                    "name for them"
                )
            schemas.setdefault(
                message_key, _discriminated_union(types, schema_map, schemas)
            )
            json_schema = {"$ref": f"#/components/schemas/{message_key}"}
        operation_key = _operation_key(topic_data)
        channel_key = _channel_key(topic_data.topic)
        channel_ref = f"#/channels/{channel_key}"
        message_ref = f"#/components/messages/{message_key}"

        if message_key not in messages:
            messages[message_key] = Message(
                payload=Schema(**json_schema),
                **{
                    "x-zero-component-type": topic_data.component_type,
                },  # type: ignore
            )

        operation = Operation(
            action=topic_data.direction, channel=Reference(**{"$ref": channel_ref})
        )

        yard_tag = (
            {"x-zero-yard-tag": topic_data.yard_tag} if topic_data.yard_tag else {}
        )
        channel = Channel(
            address=topic_data.topic,
            messages=Messages(root={"message": Reference(**{"$ref": message_ref})}),
            **{
                "x-ttl": CHANNEL_TTL,
                "x-zero-component-type": topic_data.component_type,
                **yard_tag,
            },  # type: ignore
        )

        if channel_key in channels:
            warning(
                "Channel id %s is already taken, this should not happen", channel_key
            )

        if operation_key in operations:
            warning(
                "Operation id %s is already taken, this should not happen",
                operation_key,
            )

        channels[channel_key] = channel
        operations[operation_key] = operation

    return AsyncAPI3(
        asyncapi="3.0.0",
        info=Info(title=title, version=version),
        defaultContentType="application/json",
        servers=Servers(
            {
                "broker": Server(
                    host="localhost",
                    protocol="mqtt",
                    protocolVersion="5.0",
                )
            }
        ),
        channels=Channels(root=channels),
        operations=Operations(root=operations),
        components=Components(
            messages=Messages(root=messages), schemas=Schemas(root=schemas)
        ),
    )


def generate_asyncapi(
    config: Config,
    *,
    title: str = "THRS Control",
    version: str = "1.0.0",
) -> AsyncAPI3:
    """
    The document of the thrs mode's controllers, which has every module, and of the simulator in
    every simulation mode.
    """
    thrs_mode = lookup_mode("thrs")
    simulation_modes = [mode for mode in MODES if mode.simulation_description]
    topics = collect_topics(config, thrs_mode, simulation_modes)

    return _build_asyncapi(
        title, version, thrs_mode, topics, simulation_union_names(config)
    )
