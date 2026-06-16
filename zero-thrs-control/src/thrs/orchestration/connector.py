import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Protocol

from aiomqtt import Client, Topic
from pydantic.fields import FieldInfo

from thrs.input_output.base import CombinedValues, ThrsValues, get_topic
from thrs.input_output.model_builder import CombinedModelBuilder, PartialModelBuilder
from thrs.orchestration.module import ModuleClassMap
from thrs.orchestration.simulation import ExecutionResult, Simulation, SimulationResult
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)


class MqttMapping[M](Protocol):
    """Mapping between a model and MQTT topics"""

    def split_to_topics(self, model: M) -> dict[str, str]: ...

    def subscribe_topics(self) -> set[str]: ...

    def handle_message(self, topic: str, json: str | bytes): ...

    def result(self) -> M | None: ...


class PartialMqttMapping[M: ThrsValues](MqttMapping[M]):
    """
    MQTT mapping that maps each component in the model to a separate topic.

    Those topics can either be part of a specific topic base or can be configured to be entirely different.
    """

    def __init__(self, cls: type[M], topic_prefix: str, module_prefix: str):
        self._cls = cls
        self._topic_prefix = topic_prefix
        self._module_prefix = module_prefix
        self._subscribe_topics = {
            f"{self._topic_prefix}/{
                (get_topic(field) or f'{self._module_prefix}/+')
            }": field_name
            for field_name, field in cls.model_fields.items()
        }
        self.topic_to_field = {
            self._topic(field_name, field): field_name
            for field_name, field in cls.model_fields.items()
        }
        self._builder = PartialModelBuilder(self._cls)

    def split_to_topics(self, model: M) -> dict[str, str]:
        return {
            self._topic(key, field): getattr(model, key).model_dump_json(by_alias=True)
            for key, field in self._cls.model_fields.items()
        }

    def _topic(self, key: str, field: FieldInfo) -> str:
        return f"{self._topic_prefix}/{
            (get_topic(field) or f'{self._module_prefix}/{hyphenize(key)}')
        }"

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

    def __init__(self, clss: ModuleClassMap, topic_prefix: str = ""):
        self._clss = clss
        self._topic_prefix = topic_prefix
        self._plain_mappings: Mapping[str, PartialMqttMapping] = {
            name: PartialMqttMapping(module_cls, topic_prefix, name)
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
    async def start(self): ...
    async def transceive(self, control_values: C) -> ExecutionResult[S]: ...

    @property
    def start_time(self) -> datetime: ...

    def time(self) -> datetime: ...


class MqttControlConnector(Connector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        mqtt_client: Client,
        topic_prefix: str,
        sensor_values_clss: ModuleClassMap,
        control_values_clss: ModuleClassMap,
        control_topic_suffix: str | None = None,
        start_time: datetime | None = None,
    ):
        self._start_time = start_time or datetime.now()
        self._mqtt_client = mqtt_client
        self._topic_prefix = topic_prefix
        self._control_topic_suffix_str = (
            f"/{control_topic_suffix}" if control_topic_suffix else ""
        )
        self._sensor_values_mqtt_mapping = ModuleMqttMapping(
            sensor_values_clss, topic_prefix
        )
        self._control_values_mqtt_mapping = ModuleMqttMapping(
            control_values_clss, topic_prefix
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

    async def _publish_by_mapping[T](
        self, client: Client, mapping: MqttMapping[T], value: T
    ):
        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            topic = f"{topic}{self._control_topic_suffix_str}"
            await client.publish(topic, payload, qos=1)

    def _clean_topic(self, topic: Topic) -> str:
        return topic.value.removeprefix(f"{self._topic_prefix}/")

    async def _send_control_values(self, control_values: CombinedValues):
        logging.debug("Publishing control values")
        await self._publish_by_mapping(
            self._mqtt_client,
            self._control_values_mqtt_mapping,
            control_values,
        )

    async def start(self):
        for topic in self._sensor_values_mqtt_mapping.subscribe_topics():
            await self._mqtt_client.subscribe(topic, qos=1)

    async def run(self):
        self._running = True
        try:
            await self._listen_to_sensors()
        finally:
            self._running = False

    async def transceive(
        self, control_values: CombinedValues
    ) -> ExecutionResult[CombinedValues]:
        if not self._running:
            raise Exception(
                "MqttControlConnector not running, run() should be called in a create_task()"
            )
        sensors = self._sensor_values_mqtt_mapping.result()
        await self._send_control_values(control_values)

        return ExecutionResult(
            timestamp=datetime.now(),
            sensor_values=sensors if sensors else CombinedValues(values={}),
        )

    @property
    def start_time(self) -> datetime:
        return self._start_time

    def time(self) -> datetime:
        return datetime.now()


class MqttSimulationConnector(Connector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        simulation: "Simulation",
        mqtt_client: Client,
        topic_prefix: str,
        sensor_values_clss: ModuleClassMap,
        simulation_outputs_cls: type[ThrsValues],
    ):
        self._simulation = simulation
        self._mqtt_client = mqtt_client
        self._topic_prefix = topic_prefix
        self._sensor_values_mqtt_mapping = ModuleMqttMapping(
            sensor_values_clss, topic_prefix
        )
        self._simulation_outputs_mqtt_mapping = DirectMqttMapping(
            simulation_outputs_cls, f"{topic_prefix}/simulation/outputs"
        )

    async def _publish_by_mapping[T](
        self, client: Client, mapping: MqttMapping[T], value: T
    ):
        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            await client.publish(topic, payload, qos=1)

    async def _send_model(
        self, client: Client, model: ThrsValues, topic_suffix: str | None = None
    ):
        for key in type(model).model_fields.keys():
            value = getattr(model, key)
            topic = (
                f"{self._topic_prefix}/{hyphenize(key)}"
                if topic_suffix is None
                else f"{self._topic_prefix}/{hyphenize(key)}/{topic_suffix}"
            )

            await client.publish(
                topic,
                value.model_dump_json(),
                qos=1,
            )

    async def _send_sensor_values(
        self, execution_result: ExecutionResult[CombinedValues]
    ):
        logging.debug("Publishing sensor values")
        await self._publish_by_mapping(
            self._mqtt_client,
            self._sensor_values_mqtt_mapping,
            execution_result.sensor_values,
        )

    async def start(self):
        pass

    async def transceive(
        self, control_values: CombinedValues
    ) -> ExecutionResult[CombinedValues]:
        logging.debug("Executing simulation")
        simulation_result = self._simulation.tick(control_values)
        logging.debug("Simulation tick completed")
        await self._send_sensor_values(simulation_result)

        if isinstance(simulation_result, SimulationResult):
            logging.debug("Publishing simulation output values")
            await self._publish_by_mapping(
                self._mqtt_client,
                self._simulation_outputs_mqtt_mapping,
                simulation_result.simulation_outputs,
            )

        return simulation_result

    @property
    def start_time(self) -> datetime:
        return self._simulation.start_time

    def time(self) -> datetime:
        return self._simulation.time()


class MqttConnector(Connector[CombinedValues, CombinedValues]):
    # Compatibility wrapper composed from split connectors:
    # - MqttControlConnector handles controller-side MQTT I/O
    # - MqttSimulationConnector handles simulation-side execution and publishing
    def __init__(
        self,
        simulation: "Simulation",
        controller_client: Client,
        environment_client: Client,
        topic_prefix: str,
        sensor_values_clss: ModuleClassMap,
        control_values_clss: ModuleClassMap,
        simulation_outputs_cls: type[ThrsValues],
        control_topic_suffix: str | None = None,
    ):
        self._control_connector = MqttControlConnector(
            mqtt_client=controller_client,
            topic_prefix=topic_prefix,
            sensor_values_clss=sensor_values_clss,
            control_values_clss=control_values_clss,
            control_topic_suffix=control_topic_suffix,
        )
        self._simulation_connector = MqttSimulationConnector(
            simulation=simulation,
            mqtt_client=environment_client,
            topic_prefix=topic_prefix,
            sensor_values_clss=sensor_values_clss,
            simulation_outputs_cls=simulation_outputs_cls,
        )

    async def start(self):
        await self._control_connector.start()

    async def run(self):
        await self._control_connector.run()

    async def transceive(
        self, control_values: CombinedValues
    ) -> ExecutionResult[CombinedValues]:
        await self._control_connector.transceive(control_values)
        return await self._simulation_connector.transceive(control_values)

    @property
    def start_time(self) -> datetime:
        return self._simulation_connector.start_time

    def time(self) -> datetime:
        return self._simulation_connector.time()
