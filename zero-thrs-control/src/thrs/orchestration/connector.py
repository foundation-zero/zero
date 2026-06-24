import logging
from collections.abc import Mapping
from typing import Protocol

from aiomqtt import Client
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.input_output.base import CombinedValues, ThrsValues, get_topic
from thrs.input_output.model_builder import CombinedModelBuilder, PartialModelBuilder
from thrs.orchestration.module import ModuleClassMap
from thrs.orchestration.simulation import Simulation, SimulationResult
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
    async def transceive(self, control_values: C) -> S: ...


class MqttConnector(Connector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        mqtt_client: Client,
        devices_topic_prefix: str,
        controller_topic_prefix: str,
        sensor_values_clss: ModuleClassMap,
        control_values_clss: ModuleClassMap,
        control_topic_suffix: str | None = None,
    ):
        self._mqtt_client = mqtt_client
        self._sensor_values_mqtt_mapping = ModuleMqttMapping(
            sensor_values_clss, devices_topic_prefix
        )
        self._control_values_mqtt_mapping = ModuleMqttMapping(
            control_values_clss, devices_topic_prefix, control_topic_suffix
        )
        self._computed_values_mqtt_mapping = ModuleMqttMapping(
            sensor_values_clss, controller_topic_prefix, only_computed_fields=True
        )

        self._running = False

    async def _listen_to_sensors(self):
        async for message in self._mqtt_client.messages:
            if not any(
                message.topic.matches(topic)
                for topic in self._sensor_values_mqtt_mapping.subscribe_topics()
            ):
                continue
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            self._sensor_values_mqtt_mapping.handle_message(
                message.topic.value, message.payload
            )

    async def _publish_by_mapping[T](self, mapping: MqttMapping[T], value: T):
        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            logging.debug("Publishing on %s", topic)
            await self._mqtt_client.publish(topic, payload, qos=1)

    async def _send_control_values(self, control_values: CombinedValues):
        logging.debug("Publishing control values")
        await self._publish_by_mapping(
            self._control_values_mqtt_mapping, control_values
        )

    async def _send_computed_values(self, sensor_values: CombinedValues | None):
        if sensor_values is None:
            return

        logging.debug("Publishing computed values")
        await self._publish_by_mapping(
            self._computed_values_mqtt_mapping, sensor_values
        )

    async def _start(self):
        for topic in self._sensor_values_mqtt_mapping.subscribe_topics():
            await self._mqtt_client.subscribe(topic, qos=1)

    async def run(self):
        self._running = True
        try:
            await self._start()
            await self._listen_to_sensors()
        finally:
            self._running = False

    async def transceive(self, control_values: CombinedValues) -> CombinedValues:
        if not self._running:
            raise Exception(
                "MqttControlConnector not running, run() should be called in a create_task()"
            )
        sensors_values = self._sensor_values_mqtt_mapping.result()
        await self._send_computed_values(sensors_values)
        await self._send_control_values(control_values)

        return sensors_values if sensors_values else CombinedValues(values={})


class MqttSimulationConnector(Connector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        simulation: "Simulation",
        mqtt_client: Client,
        devices_topic_prefix: str,
        simulation_topic_prefix: str,
        sensor_values_clss: ModuleClassMap,
        simulation_outputs_cls: type[ThrsValues],
    ):
        self._simulation = simulation
        self._mqtt_client = mqtt_client
        self._sensor_values_mqtt_mapping = ModuleMqttMapping(
            sensor_values_clss, devices_topic_prefix
        )
        self._simulation_outputs_mqtt_mapping = DirectMqttMapping(
            simulation_outputs_cls, f"{simulation_topic_prefix}/outputs"
        )

    async def _publish_by_mapping[T](self, mapping: MqttMapping[T], value: T):
        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            logging.debug("Publishing on %s", topic)
            await self._mqtt_client.publish(topic, payload, qos=1)

    async def _send_sensor_values(self, execution_result: SimulationResult):
        logging.debug("Publishing sensor values")
        await self._publish_by_mapping(
            self._sensor_values_mqtt_mapping,
            execution_result.sensor_values,
        )

    async def _send_simulation_output(self, simulation_result: SimulationResult):
        logging.debug("Publishing simulation output values")
        await self._publish_by_mapping(
            self._simulation_outputs_mqtt_mapping,
            simulation_result.simulation_outputs,
        )

    async def run(self):
        pass

    async def transceive(self, control_values: CombinedValues) -> CombinedValues:
        logging.debug("Executing simulation")
        simulation_result = self._simulation.tick(control_values)

        logging.debug("Simulation tick completed")
        await self._send_sensor_values(simulation_result)
        await self._send_simulation_output(simulation_result)

        return simulation_result.sensor_values
