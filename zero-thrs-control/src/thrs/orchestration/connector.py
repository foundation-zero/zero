import asyncio
import logging
from collections.abc import AsyncIterator, Mapping
from enum import Enum
from typing import Protocol

from aiomqtt import Client, Message
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.input_output.base import (
    CombinedValues,
    SimulationValues,
    ThrsValues,
    get_topic,
)
from thrs.input_output.model_builder import CombinedModelBuilder, PartialModelBuilder
from thrs.orchestration.module import ModuleClassMap
from thrs.orchestration.simulation import SimulationResult
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)


class ConnectorListeningMode(Enum):
    SENSORS = 1
    CONTROLS = 2
    NONE = 3


class NoneMessageIterator(AsyncIterator[Message]):
    """Async iterator that never yields anything. Behaves like an
    infinite, empty MQTT listener without doing actual work"""

    def __aiter__(self) -> AsyncIterator[Message]:
        return self

    async def __anext__(self) -> Message:
        await asyncio.Event().wait()  # blocks forever, cancelable
        raise AssertionError("unreachable")


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
    async def send_control(self, control_values: C) -> None: ...
    async def get_sensor_values(
        self,
    ) -> S: ...

    async def get_control_values(self) -> C: ...

    async def send_computed_sensor_values(self, sensors_values: S) -> None: ...
    async def send_sensor_values(self, simulation_result: SimulationResult) -> None: ...
    async def send_simulation_values(
        self, simulation_result: SimulationResult
    ) -> None: ...


class MqttConnector(Connector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        mqtt_client: Client,
        listening_mode: ConnectorListeningMode,
        devices_topic_prefix: str,
        controller_topic_prefix: str,
        sensor_values_clss: ModuleClassMap,
        control_values_clss: ModuleClassMap,
        controller_state_clss: ModuleClassMap,
        simulation_outputs_clss: type[SimulationValues] | None = None,
        control_topic_suffix: str | None = None,
        sensor_topic_suffix: str | None = None,
        simulation_topic_prefix: str | None = None,
    ):
        self._mqtt_client = mqtt_client
        self._listening_mode = listening_mode
        self._sensor_values_mqtt_mapping = ModuleMqttMapping(
            sensor_values_clss, devices_topic_prefix, sensor_topic_suffix
        )
        self._control_values_mqtt_mapping = ModuleMqttMapping(
            control_values_clss, devices_topic_prefix, control_topic_suffix
        )
        self._computed_values_mqtt_mapping = ModuleMqttMapping(
            sensor_values_clss, controller_topic_prefix, only_computed_fields=True
        )
        self._controller_state_mqtt_mapping = ModuleMqttMapping(
            controller_state_clss, controller_topic_prefix
        )
        self._simulation_outputs_mqtt_mapping = (
            DirectMqttMapping(simulation_outputs_clss, simulation_topic_prefix or "")
            if simulation_outputs_clss is not None
            else None
        )
        self._running = False

    async def _subscribe_mapped_topics(self, mapping: ModuleMqttMapping | None):
        if mapping is None:
            return

        for topic in mapping.subscribe_topics():
            await self._mqtt_client.subscribe(topic, qos=1)

    async def run(self):
        """Run the connector, subscribing and listening to MQTT messages - handling them according to the mapping."""
        self._running = True
        try:
            mapping: ModuleMqttMapping | None = self._get_module_mapping_for_listener()

            await self._subscribe_mapped_topics(mapping)
            await self._listen_to(mapping)
        finally:
            self._running = False

    def _get_module_mapping_for_listener(self) -> None:
        """Start listening to MQTT messages, listening mode controls
        whether to listen to sensor values or control values."""
        match self._listening_mode:
            case ConnectorListeningMode.SENSORS:
                return self._sensor_values_mqtt_mapping
            case ConnectorListeningMode.CONTROLS:
                return self._control_values_mqtt_mapping
            case ConnectorListeningMode.NONE:
                return None
            case _: # Future failsafe, in case new listening modes are added and not handled here
                raise ValueError(f"Unsupported listening mode: {self._listening_mode}. Please add a case for it in {self._get_module_mapping_for_listener.__qualname__}")

    async def _listen_to(self, mapping: "MqttMapping | None") -> None:
        """Listen to MQTT messages and handle them according to the mapping."""
        message_iterator = self._get_message_iterator(mapping)

        async for message in message_iterator:
            if mapping is None:
                continue

            if not any(
                message.topic.matches(topic) for topic in mapping.subscribe_topics()
            ):
                continue

            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )

            mapping.handle_message(message.topic.value, message.payload)

    def _get_message_iterator(self, mapping):
        """Get the message iterator for the MQTT client, or a NoneMessageIterator if no mapping is provided to ensure an equal working interface."""
        message_iterator: AsyncIterator[Message] = self._mqtt_client.messages

        if mapping is None:
            message_iterator = NoneMessageIterator()
        return message_iterator

    def _guard_running(self):
        if not self._running:
            raise Exception(
                "MqttControlConnector not running, run() should be called in a create_task()"
            )

    async def _publish_by_mapping[T](self, mapping: MqttMapping[T], value: T):
        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            logging.debug("Publishing on %s", topic)
            await self._mqtt_client.publish(topic, payload, qos=1)

    async def _send_control(self, control_values: CombinedValues):
        logging.debug("Publishing control values")
        await self._publish_by_mapping(
            self._control_values_mqtt_mapping, control_values
        )

    async def _send_sensor_values(self, simulation_result: SimulationResult):
        logging.debug("Publishing sensor values")
        await self._publish_by_mapping(
            self._sensor_values_mqtt_mapping, simulation_result.sensor_values
        )

    async def _send_simulation_outputs(self, simulation_result: SimulationResult):
        if not self._simulation_outputs_mqtt_mapping:
            raise Exception("Simulation outputs mapping not configured")
        logging.debug("Publishing simulation outputs")
        await self._publish_by_mapping(
            self._simulation_outputs_mqtt_mapping, simulation_result.simulation_outputs
        )

    async def _send_computed_sensor_values(self, sensor_values: CombinedValues | None):
        if sensor_values is None:
            return

        logging.debug("Publishing computed sensor values")
        await self._publish_by_mapping(
            self._computed_values_mqtt_mapping, sensor_values
        )

    async def _send_controller_state(self, controller_state: CombinedValues):
        logging.debug("Publishing controller values")
        await self._publish_by_mapping(
            self._controller_state_mqtt_mapping, controller_state
        )

    async def _get_control_values_from_mqtt(self) -> CombinedValues | None:
        return (
            self._control_values_mqtt_mapping.result()
        )  # TODO: Maapater, does this work?

    async def send_computed_sensor_values(self, sensors_values: CombinedValues) -> None:
        self._guard_running()
        await self._send_computed_sensor_values(sensors_values)

    async def send_control(self, control_values: CombinedValues) -> None:
        self._guard_running()
        await self._send_control(control_values)

    async def send_sensor_values(self, simulation_result: SimulationResult):
        self._guard_running()
        logging.debug("Publishing sensor values")
        await self._send_sensor_values(simulation_result)

    async def send_simulation_values(self, simulation_result: SimulationResult):
        self._guard_running()
        logging.debug("Publishing simulation outputs")
        await self._send_simulation_outputs(simulation_result)

    async def get_sensor_values(self) -> CombinedValues:
        self._guard_running()
        sensors_values = self._sensor_values_mqtt_mapping.result()
        return sensors_values if sensors_values else CombinedValues(values={})

    async def get_control_values(self) -> CombinedValues:
        self._guard_running()
        control_values = self._control_values_mqtt_mapping.result()
        return control_values if control_values else CombinedValues(values={})
