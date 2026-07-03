import logging
from collections.abc import AsyncIterator, Mapping
from typing import Protocol

from aiomqtt import Client, Message
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.input_output.base import (
    CombinedValues,
    ThrsValues,
    get_topic,
)
from thrs.input_output.model_builder import CombinedModelBuilder, PartialModelBuilder
from thrs.orchestration.module import ModuleClassMap
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)


class MqttMapping[M](Protocol):
    """Mapping between a model and MQTT topics"""

    def split_to_topics(self, model: M) -> dict[str, str]:
        """Split model instance values to topics and payloads.

        Args:
            model: ThrsValues subclass with values to publish

        Returns:
            dict[str, str]: mapping with topics and their payloads to publish
        """
        ...

    def subscribe_topics(self) -> set[str]: ...

    def handle_message(self, topic: str, json: str | bytes): ...

    def result(self) -> M | None: ...


class PartialMqttMapping[M: ThrsValues](MqttMapping[M]):
    """
    MQTT mapping that maps each component in the model to a separate topic.

    Those topics can either be part of a specific topic base or can be configured to be entirely different.
    """

    def __init__(
        self,
        cls: type[M],
        topic_prefix: str,
        module_prefix: str,
        topic_suffix: str | None = None,
        *,
        only_computed_fields: bool = False,
    ):
        self._cls = cls
        self._topic_prefix = topic_prefix
        self._module_prefix = module_prefix
        self._topic_suffix_str = f"/{topic_suffix}" if topic_suffix else ""
        self._only_computed_fields = only_computed_fields
        self._subscribe_topics = {
            self._topic("+", field): field_name
            for field_name, field in cls.model_fields.items()
        }
        self.topic_to_field = {
            self._topic(field_name, field): field_name
            for field_name, field in cls.model_fields.items()
        }
        self._builder = PartialModelBuilder(self._cls)

    def split_to_topics(self, model: M) -> dict[str, str]:
        fields = (
            self._cls.model_computed_fields
            if self._only_computed_fields
            else self._cls.model_fields
        )
        return {
            self._topic(key, field): getattr(model, key).model_dump_json(by_alias=True)
            for key, field in fields.items()
        }

    def _topic(self, key: str, field: FieldInfo | ComputedFieldInfo) -> str:
        return f"{self._topic_prefix}/{(get_topic(field) or f'{self._module_prefix}/{hyphenize(key)}')}{self._topic_suffix_str}"

    def subscribe_topics(self) -> set[str]:
        return set(self._subscribe_topics.keys())

    def handle_message(self, topic: str, json: str | bytes):
        if topic not in self.topic_to_field:
            return

        self._builder.input(self.topic_to_field[topic], json)

    def result(self) -> M | None:
        return self._builder.result()


class DirectMqttMapping[M: ThrsValues](MqttMapping[M]):
    """MQTT mapping that maps the entire model to a single topic"""

    def __init__(self, cls: type[M], topic_prefix: str):
        self._cls = cls
        self._topic = topic_prefix
        self._value = None

    def split_to_topics(self, model: M) -> dict[str, str]:
        return {self._topic: model.model_dump_json(by_alias=True)}

    def subscribe_topics(self) -> set[str]:
        return set(self._topic)

    def handle_message(self, topic: str, json: str | bytes):
        if topic == self._topic:
            self._value = self._cls.model_validate_json(json)

    def result(self) -> M | None:
        return self._value


class ModuleMqttMapping(MqttMapping[CombinedValues]):
    """
    MQTT mapping for modules

    Accepts a `ModuleClassMap` instead of a single class.
    Delegates to `PartialMqttMapping` for each sub-model.
    """

    def __init__(
        self,
        clss: ModuleClassMap,
        topic_prefix: str = "",
        topic_suffix: str | None = None,
        only_computed_fields: bool = False,
    ):
        self._clss = clss
        self._topic_prefix = topic_prefix
        self._plain_mappings: Mapping[str, PartialMqttMapping] = {
            name: PartialMqttMapping(
                module_cls,
                topic_prefix,
                name,
                topic_suffix,
                only_computed_fields=only_computed_fields,
            )
            for name, module_cls in clss.items()
        }
        self._topic_mappings = {
            topic: f"{name}/{field}"
            for name in self._clss
            for topic, field in self._plain_mappings[name].topic_to_field.items()
        }
        self._builder = CombinedModelBuilder(self._clss)

    def split_to_topics(self, model: CombinedValues) -> dict[str, str]:
        return {
            topic: value
            for module, model in model.values.items()
            for topic, value in self._plain_mappings[module]
            .split_to_topics(model)
            .items()
        }

    def subscribe_topics(self) -> set[str]:
        return {
            topic
            for mapping in self._plain_mappings.values()
            for topic in mapping.subscribe_topics()
        }

    def handle_message(self, topic: str, json: str | bytes):
        field = self._topic_mappings[topic]
        self._builder.input(field, json)

    def result(self) -> CombinedValues | None:
        return self._builder.result()


class Connector[S, C](Protocol):
    async def run(self): ...
    async def get_input_values(self) -> S: ...
    async def send_output(self, values: C) -> None: ...
    async def send_computed_input(self, computed_values: S) -> None: ...
    async def send_controller_state(self, values: CombinedValues) -> None: ...


class MqttConnector(Connector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        mqtt_client: Client,
        devices_topic_prefix: str,
        controller_state_output_clss: ModuleClassMap,
        input_values_clss: ModuleClassMap,
        output_values_clss: ModuleClassMap,
        controller_state_output_topic_prefix: str,
        output_topic_suffix: str | None = None,
        input_topic_suffix: str | None = None,
    ):
        self.controller_state_output_clss = controller_state_output_clss

        self._mqtt_client = mqtt_client
        self._input_values_mqtt_mapping = ModuleMqttMapping(
            input_values_clss, devices_topic_prefix, input_topic_suffix
        )
        self._output_values_mqtt_mapping = ModuleMqttMapping(
            output_values_clss, devices_topic_prefix, output_topic_suffix
        )
        self._computed_values_mqtt_mapping = ModuleMqttMapping(
            input_values_clss,
            controller_state_output_topic_prefix,
            only_computed_fields=True,
        )
        self._controller_state_mqtt_mapping = ModuleMqttMapping(
            controller_state_output_clss, controller_state_output_topic_prefix
        )
        self._running = False

    async def run(self):
        """Run the connector, subscribing and listening to MQTT messages - handling them according to the mapping."""
        self._running = True
        try:
            await self._subscribe_mapped_topics(self._input_values_mqtt_mapping)
            await self._listen_for_input_values(self._input_values_mqtt_mapping)
        finally:
            self._running = False

    async def _subscribe_mapped_topics(self, mapping: ModuleMqttMapping):
        for topic in mapping.subscribe_topics():
            await self._mqtt_client.subscribe(topic, qos=1)

    async def _listen_for_input_values(self, mapping: ModuleMqttMapping) -> None:
        """Listen to MQTT messages and handle them according to the mapping."""

        message_iterator: AsyncIterator[Message] = self._mqtt_client.messages

        async for message in message_iterator:
            if not any(
                message.topic.matches(topic) for topic in mapping.subscribe_topics()
            ):
                continue

            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )

            mapping.handle_message(message.topic.value, message.payload)

    def _guard_running(self):
        if not self._running:
            raise Exception(
                "MqttConnector not running, run() should be called in a create_task()"
            )

    async def _publish_by_mapping[T](self, mapping: MqttMapping[T], value: T):
        self._guard_running()

        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            logging.debug("Publishing on %s", topic)
            await self._mqtt_client.publish(topic, payload, qos=1)

    async def _send_output(self, output_values: CombinedValues):
        logging.debug("Publishing values")
        await self._publish_by_mapping(self._output_values_mqtt_mapping, output_values)

    async def _send_input_computed_values(self, computed_values: CombinedValues):
        logging.debug("Publishing computed values")
        await self._publish_by_mapping(
            self._computed_values_mqtt_mapping, computed_values
        )

    async def _send_controller_state(self, controller_state: CombinedValues):
        logging.debug("Publishing controller state values")
        await self._publish_by_mapping(
            self._controller_state_mqtt_mapping, controller_state
        )

    async def get_input_values(self) -> CombinedValues:
        input_values = self._input_values_mqtt_mapping.result()
        return input_values if input_values else CombinedValues(values={})

    async def send_output(self, values: CombinedValues) -> None:
        await self._send_output(values)

    async def send_computed_input(self, values: CombinedValues) -> None:
        await self._send_input_computed_values(values)

    async def send_controller_state(self, values: CombinedValues) -> None:
        await self._send_controller_state(values)
