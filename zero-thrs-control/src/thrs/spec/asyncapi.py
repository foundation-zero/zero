"""The AsyncAPI 3.0 document of the THRS control system.

Channels are recorded from the runtime's own channel wiring, so the document cannot drift from it.
"""

from collections.abc import Mapping
from logging import warning

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
from pydantic.json_schema import JsonSchemaMode, models_json_schema

from thrs.input_output.base import ThrsValues
from thrs.orchestration.config import Config
from thrs.runtime.descriptions.simulation import Mode
from thrs.spec.recording_connector import TopicMapping, collect_topics

# As in thrs-api, a served value never expires into null.
CHANNEL_TTL = "1h"


def _channel_key(topic: str) -> str:
    return topic.replace("/", "_")


def _operation_key(topic: TopicMapping) -> str:
    return topic.topic.replace("/", "_")


def _message_key(payload_type: type[ThrsValues]) -> str:
    return f"{payload_type.__module__.split('.')[-1]}{payload_type.__name__.replace('[', '').replace(']', '')}"


def _build_asyncapi(
    title: str, version: str, mode: Mode, topics: list[TopicMapping]
) -> AsyncAPI3:
    """The document for the registered (template, direction) groups."""

    payloads: list[tuple[type[ThrsValues], JsonSchemaMode]] = [
        (topic_data.payload_type, "serialization") for topic_data in topics
    ]
    schema_map, defs = models_json_schema(
        payloads,
        by_alias=True,
        ref_template="#/components/schemas/{model}",
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

    messages: Mapping[str, Message | Reference] = {}
    for topic_data in sorted(topics, key=lambda topic: topic.topic):
        message_key = _message_key(topic_data.payload_type)
        operation_key = _operation_key(topic_data)
        channel_key = _channel_key(topic_data.topic)
        channel_ref = f"#/channels/{channel_key}"
        message_ref = f"#/components/messages/{message_key}"

        if message_key not in messages:
            json_schema = schema_map[(topic_data.payload_type, "serialization")]
            messages[message_key] = Message(
                payload=Schema(**json_schema),
                **{
                    "x-zero-component-type": topic_data.component_type,
                },  # type: ignore
            )

        operation = Operation(
            action=topic_data.direction, channel=Reference(**{"$ref": channel_ref})
        )

        channel = Channel(
            address=topic_data.topic,
            messages=Messages(root={"message": Reference(**{"$ref": message_ref})}),
            **{
                "x-ttl": CHANNEL_TTL,
                "x-zero-component-type": topic_data.component_type,
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
    mode: Mode,
    *,
    title: str = "THRS Control",
    version: str = "1.0.0",
) -> AsyncAPI3:
    topics = collect_topics(config, mode)

    return _build_asyncapi(title, version, mode, topics)
