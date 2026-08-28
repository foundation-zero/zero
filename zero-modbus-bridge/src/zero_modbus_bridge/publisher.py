"""MQTT publisher: registers FastStream publishers and dispatches payloads."""

import asyncio
import logging
import re
from typing import TYPE_CHECKING, Any, Protocol, cast

from faststream._internal.broker.registrator import Registrator
from faststream.mqtt import MQTTBroker, QoS
from faststream.mqtt.publisher.config import (
    MQTTPublisherConfig,
    MQTTPublisherSpecificationConfig,
)
from faststream.mqtt.publisher.specification import MQTTPublisherSpecification
from faststream.mqtt.publisher.usecase import MQTTPublisher
from pydantic import BaseModel

from zero_modbus_bridge.io import ModbusTopic

if TYPE_CHECKING:
    from faststream.mqtt.broker.config import MQTTBrokerConfig
    from faststream.specification.schema import PublisherSpec

logger = logging.getLogger(__name__)


def _register(broker: MQTTBroker, publisher: MQTTPublisher) -> None:
    """Register a pre-built publisher via the base registrator."""
    Registrator.publisher(cast("Registrator[Any, Any]", broker), publisher)


class TopicPublisher(Protocol):
    """Minimal publisher contract the bridge depends on."""

    async def publish(self, topic: str, payload: BaseModel) -> None: ...


class MappingPublisher:
    """Wraps a ``TopicPublisher`` to map read-model payloads to publish-model payloads.

    Keeps ``ModbusBridge`` generic - reading uses ``AnnotationModbusTopic`` with
    ``ModbusField`` metadata, publishing uses a separate MQTT schema. The bridge
    still loops ``read_all()->publish()`` unchanged; the mapper runs inside the
    publisher.
    """

    def __init__(
        self,
        inner: "TopicPublisher",
        mapper: Any,
    ):
        self._inner = inner
        self._mapper = mapper
        self._mappers: dict[str, Any] | None = mapper if isinstance(mapper, dict) else None

    async def publish(self, topic: str, payload: BaseModel) -> None:
        """Map ``payload`` then delegate to ``inner``."""
        if self._mappers is not None:
            fn = self._mappers.get(topic)
            mapped = fn(payload) if fn is not None else payload
        else:
            mapped = self._mapper(payload)  # type: ignore[operator]
        await self._inner.publish(topic, mapped)


class MqttPublisher:
    """Wraps FastStream topic publishers for a set of ModbusTopics.

    Call ``register_publishers`` once per broker to create all publishers,
    then ``publish(topic, payload)`` to send a JSON payload.
    """

    def __init__(
        self,
        broker: MQTTBroker,
        topics: list[ModbusTopic],
        *,
        schemas: dict[str, type[BaseModel]] | None = None,
    ):
        self._publishers = self.register_publishers(broker, topics, schemas)

    @staticmethod
    def register_publishers(
        broker: MQTTBroker,
        topics: list[ModbusTopic],
        schemas: dict[str, type[BaseModel]] | None = None,
    ) -> dict[str, MQTTPublisher]:
        """Register one FastStream publisher per topic, return ``topic→publisher`` dict.

        ``schemas`` overrides the AsyncAPI payload schema per topic; by
        default each publisher declares its topic's own model.
        """
        publishers: dict[str, MQTTPublisher] = {}
        for topic in topics:
            publisher = broker.publisher(
                topic.topic,
                schema=(schemas or {}).get(topic.topic, topic.model),
                qos=QoS.AT_LEAST_ONCE,
                description=f"Modbus data for {topic.topic}",
            )
            publishers[topic.topic] = publisher
        return publishers

    async def publish(self, topic: str, payload: BaseModel) -> None:
        """Publish a JSON payload to a previously-registered topic."""
        if publisher := self._publishers.get(topic):
            await publisher.publish(payload)
        else:
            logger.warning("No publisher for topic %s", topic)


class ParametrizedPublisherSpecification(MQTTPublisherSpecification):
    """AsyncAPI schema for a parametrized topic template.

    FastStream derives the channel key, address and bindings from the schema
    dict returned by ``get_schema`` — the key doubles as the address. Passing
    the ``{param}`` template as the title therefore yields a channel whose
    address *is* the template; this subclass only rewrites the MQTT binding
    topic to its wildcard form.
    """

    def __init__(
        self,
        _outer_config: "MQTTBrokerConfig",
        specification_config: MQTTPublisherSpecificationConfig,
        wildcard_topic: str,
    ):
        super().__init__(
            _outer_config=_outer_config, specification_config=specification_config
        )
        self._wildcard_topic = wildcard_topic

    def get_schema(self) -> "dict[str, PublisherSpec]":
        schema = super().get_schema()
        for publisher_spec in schema.values():
            if (
                publisher_spec.bindings is not None
                and publisher_spec.bindings.mqtt is not None
            ):
                publisher_spec.bindings.mqtt.topic = self._wildcard_topic
        return schema


class ParametrizedMQTTPublisher(MQTTPublisher):
    """Publisher for a parametrized topic family (`power-tags/{panel}/{slug}`).

    A real ``MQTTPublisher`` subclass: it is registered on the broker like any
    other publisher, and its specification emits a single AsyncAPI channel for
    the whole template (address = template, mqtt binding = wildcard pattern).
    Publishing goes through concrete per-topic publishers created lazily and
    validated against the declared parameter enums.

    Unlike a stock ``MQTTPublisher``, ``publish`` takes ``(topic, payload)``
    matching the bridge's ``TopicPublisher`` contract — it deliberately
    shadows the FastStream signature. The channel cannot carry a
    ``parameters`` block (the upstream AsyncAPI model has no such field yet),
    so consumers derive parameters from the channel address.
    """

    _broker: MQTTBroker

    def __init__(
        self,
        *,
        broker_config: "MQTTBrokerConfig",
        template: str,
        parameters: dict[str, dict[str, Any]],
        qos: QoS = QoS.AT_LEAST_ONCE,
        retain: bool = False,
        description: str | None = None,
        schema: type[BaseModel] | None = None,
    ):
        names = re.findall(r"\{([^{}]+)\}", template)
        if set(names) != set(parameters):
            raise ValueError(
                f"Template placeholders {sorted(names)} do not match "
                f"parameters {sorted(parameters)}"
            )

        # The title must be the template itself: FastStream uses the schema
        # dict key as both channel key and address.
        super().__init__(
            MQTTPublisherConfig(
                topic=template,
                qos=qos,
                retain=retain,
                headers=None,
                _outer_config=broker_config,
            ),
            ParametrizedPublisherSpecification(
                broker_config,
                MQTTPublisherSpecificationConfig(
                    topic=template,
                    qos=qos,
                    retain=retain,
                    schema_=schema,
                    title_=template,
                    description_=description,
                    include_in_schema=True,
                ),
                wildcard_topic=re.sub(r"\{[^{}]+\}", "+", template),
            ),
        )
        self._broker_config = broker_config
        self._parameters = parameters
        self._cache: dict[str, MQTTPublisher] = {}
        self._lock = asyncio.Lock()

    @property
    def parameters(self) -> dict[str, dict[str, Any]]:
        """Parameter enums declared for the topic family."""
        return self._parameters

    @classmethod
    def create(
        cls,
        broker: MQTTBroker,
        template: str,
        *,
        parameters: dict[str, dict[str, Any]],
        qos: QoS = QoS.AT_LEAST_ONCE,
        retain: bool = False,
        description: str | None = None,
        schema: type[BaseModel] | None = None,
    ) -> "ParametrizedMQTTPublisher":
        """Build the publisher and register it on ``broker``."""
        publisher = cls(
            broker_config=cast("MQTTBrokerConfig", broker.config),
            template=template,
            parameters=parameters,
            qos=qos,
            retain=retain,
            description=description,
            schema=schema,
        )
        # Kept for lazily registering the concrete per-topic publishers.
        publisher._broker = broker
        _register(broker, publisher)
        return publisher

    def _match(self, topic: str) -> dict[str, str] | None:
        """Resolve a concrete topic against the template, validating enums."""
        parts = re.split(r"(\{[^{}]+\})", self.topic)
        pattern = "".join(
            f"(?P<{part[1:-1]}>[^/]+)" if part.startswith("{") else re.escape(part)
            for part in parts
        )
        match = re.fullmatch(pattern, topic)
        if match is None:
            return None

        values = match.groupdict()
        for name, spec in self._parameters.items():
            allowed = spec.get("enum")
            if allowed is not None and values.get(name) not in allowed:
                return None
        return values

    async def publish(self, topic: str, payload: BaseModel) -> None:  # type: ignore[override]
        """Publish to the concrete topic, creating its publisher on first use."""
        if self._match(topic) is None:
            logger.warning("No publisher for topic %s", topic)
            return

        async with self._lock:
            publisher = self._cache.get(topic)
            if publisher is None:
                publisher = MQTTPublisher(
                    MQTTPublisherConfig(
                        topic=topic,
                        qos=self.qos,
                        retain=self.retain,
                        headers=None,
                        _outer_config=self._outer_config,
                    ),
                    MQTTPublisherSpecification(
                        _outer_config=self._outer_config,
                        specification_config=MQTTPublisherSpecificationConfig(
                            topic=topic,
                            qos=self.qos,
                            retain=self.retain,
                            schema_=None,
                            title_=None,
                            description_=None,
                            include_in_schema=False,
                        ),
                    ),
                )
                _register(self._broker, publisher)
                self._cache[topic] = publisher
        await publisher.publish(payload)


def finalize_parametrized_spec(
    doc: dict[str, Any], parameters: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Post-process a generated spec for `{param}` channels FastStream can't express.

    Two upstream gaps, both specific to `{param}` channel names:

    - ``$ref`` pointers are percent-encoded while component/channel map keys
      keep the raw braces, so ref resolution by exact string match fails.
    - channel ``parameters`` are never emitted: the field is still a TODO in
      FastStream's AsyncAPI channel models (native support is in progress
      upstream), and it cannot be injected by subclassing because the spec
      generator constructs ``Channel`` directly. Since ``Channel`` permits
      extra fields, attaching them here yields conforming output; drop this
      once FastStream emits parameters natively.
    """
    _decode_braced_refs(doc)

    for channel in doc.get("channels", {}).values():
        if "{" in channel.get("address", ""):
            channel["parameters"] = parameters
    return doc


def _decode_braced_refs(node: Any) -> None:
    """Decode percent-encoded braces in every ``$ref`` string under ``node``."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                node[key] = value.replace("%7B", "{").replace("%7D", "}")
            else:
                _decode_braced_refs(value)
    elif isinstance(node, list):
        for item in node:
            _decode_braced_refs(item)
