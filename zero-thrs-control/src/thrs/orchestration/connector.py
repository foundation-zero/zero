from dataclasses import dataclass
import logging
from collections.abc import Mapping
from typing import Awaitable, Callable, Protocol, Self

from aiomqtt import Client
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    get_topic,
)
from thrs.input_output.model_builder import CombinedModelBuilder, PartialModelBuilder
from thrs.orchestration.module import ModuleClassMap
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)


class MqttReceiveMapping[M](Protocol):
    """Mapping between a model and MQTT topics to receive messages"""

    def subscribe_topics(self) -> set[str]: ...

    def handle_message(self, topic: str, json: str | bytes): ...

    def result(self) -> M | None: ...


class MqttSendMapping[M](Protocol):
    """Mapping between a model and MQTT topics to send messages"""

    def split_to_topics(self, model: M) -> dict[str, str]: ...


class PartialMqttMapping[M: ThrsValues](MqttReceiveMapping[M], MqttSendMapping[M]):
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


class DirectMqttMapping[M: ThrsValues](MqttReceiveMapping[M], MqttSendMapping[M]):
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


class ModuleMqttMapping(MqttReceiveMapping[CombinedValues]):
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


class Connector[S, C, CV](Protocol):
    async def run(self): ...
    async def transceive(self, control_values: C, controller_state: CV) -> S: ...


type Publisher[T] = Callable[[T], Awaitable[None]]


class Channels[T](Protocol):
    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: T,
    ) -> Self: ...


@dataclass
class ControlChannelsDescription:
    sensor_values_clss: ModuleClassMap
    sensor_values_topic_prefix: str
    control_values_clss: ModuleClassMap
    controller_state_clss: ModuleClassMap
    control_values_topic_prefix: str
    control_values_topic_suffix: str | None = None


class ControlChannels(Channels[ControlChannelsDescription]):
    def __init__(
        self,
        sensor_values_mapping: ModuleMqttMapping,
        send_control_values: Publisher[CombinedValues],
        send_controller_state: Publisher[CombinedValues],
        # etc
    ):
        """Don't ever call this directly, use `MqttController#run` instead"""
        self.get_sensor_values = sensor_values_mapping.result
        self.send_control_values = send_control_values
        self.send_controller_state = send_controller_state

    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: ControlChannelsDescription,
    ) -> "ControlChannels":
        sensor_values_mapping = ModuleMqttMapping(
            description.sensor_values_clss,
            description.sensor_values_topic_prefix,
        )
        connector._register_listener(sensor_values_mapping)
        return ControlChannels(
            sensor_values_mapping,
            connector._create_publisher(
                ModuleMqttMapping(
                    description.control_values_clss,
                    description.control_values_topic_prefix,
                    description.control_values_topic_suffix,
                ),
            ),
            connector._create_publisher(
                ModuleMqttMapping(
                    description.controller_state_clss,
                    description.control_values_topic_prefix,
                    description.control_values_topic_suffix,
                ),
            ),
        )


@dataclass
class SimulationChannelsDescription[I: SimulationInputs, O: SimulationValues]:
    sensor_values_clss: ModuleClassMap
    sensor_values_topic_prefix: str
    control_values_clss: ModuleClassMap
    simulation_inputs_cls: type[I]
    simulation_outputs_cls: type[O]
    control_values_topic_prefix: str
    controller_topic_prefix: str
    control_values_topic_suffix: str | None = None


class SimulationChannels[I: SimulationInputs, O: SimulationValues](
    Channels[SimulationChannelsDescription[I, O]]
):
    def __init__(
        self,
        send_sensor_values: Publisher[CombinedValues],
        control_values_mapping: ModuleMqttMapping,
        simulation_inputs_mapping: DirectMqttMapping[I],
        send_simulation_outputs: Publisher[O],
        # etc
    ):
        """Don't ever call this directly, use `MqttController#run` instead"""
        self.send_sensor_values = send_sensor_values
        self.get_control_values = control_values_mapping.result
        self.send_simulation_outputs = send_simulation_outputs
        self.get_simulation_inputs = simulation_inputs_mapping.result

    @classmethod
    def _register(
        cls,
        connector: "MqttConnector",
        description: SimulationChannelsDescription,
    ) -> "SimulationChannels":
        control_values_mapping = ModuleMqttMapping(
            description.control_values_clss,
            description.control_values_topic_prefix,
            description.control_values_topic_suffix,
        )
        connector._register_listener(control_values_mapping)
        simulation_inputs_mapping = DirectMqttMapping(
            description.simulation_inputs_cls,
            description.controller_topic_prefix,
        )
        connector._register_listener(simulation_inputs_mapping)
        return SimulationChannels(
            connector._create_publisher(
                ModuleMqttMapping(
                    description.sensor_values_clss,
                    description.sensor_values_topic_prefix,
                ),
            ),
            control_values_mapping,
            simulation_inputs_mapping,
            connector._create_publisher(
                DirectMqttMapping(
                    description.simulation_outputs_cls,
                    description.controller_topic_prefix,
                ),
            ),
        )


class MqttConnector(Connector[CombinedValues, CombinedValues, CombinedValues]):
    def __init__(self, mqtt_client: Client):
        self._mqtt_client = mqtt_client
        self._listeners: list[MqttReceiveMapping[object]] = []

    def _register_listener(self, receiver: MqttReceiveMapping[object]) -> None:
        self._listeners.append(receiver)

    def _create_publisher[T](
        self, sender: MqttSendMapping[T]
    ) -> Callable[[T], Awaitable[None]]:
        async def _publish(value: T):
            await self._publish_by_mapping(sender, value)

        return _publish

    async def _listen(self):
        async for message in self._mqtt_client.messages:
            mapping = next(
                (
                    mapping
                    for mapping in self._listeners
                    for topic in mapping.subscribe_topics()
                    if message.topic.matches(topic)
                ),
                None,
            )
            if mapping is None:
                continue
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            mapping.handle_message(message.topic.value, message.payload)

    async def _publish_by_mapping[T](self, mapping: MqttSendMapping[T], value: T):
        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            logging.debug("Publishing on %s", topic)
            await self._mqtt_client.publish(topic, payload, qos=1)

    async def _start(self):
        for mapping in self._listeners:
            for topic in mapping.subscribe_topics():
                await self._mqtt_client.subscribe(topic, qos=1)

    async def run[T](
        self, channels_type: type[Channels[T]], description: T
    ) -> Channels[T]:
        await self._start()
        channels = channels_type._register(self, description)
        await self._listen()
        return channels
