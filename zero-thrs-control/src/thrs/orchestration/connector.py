import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Literal, Protocol

from aiomqtt import Client, Topic

from thrs.input_output.base import CombinedValues, ThrsValues
from thrs.input_output.model_builder import CombinedModelBuilder, PartialModelBuilder
from thrs.orchestration.module import ModuleClassMap
from thrs.orchestration.simulation import ExecutionResult, Simulation, SimulationResult
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)


class MqttMapping[M](Protocol):
    """Mapping between a model and MQTT topics"""

    def split_to_topics(self, model: M) -> dict[str, str]: ...

    def has(self, topic: str) -> bool: ...

    def subscribe_topic(self) -> str: ...

    def handle_message(self, topic: str, json: str | bytes): ...

    def result(self) -> M | None: ...


class PartialMqttMapping[M: ThrsValues](MqttMapping[M]):
    """MQTT mapping that maps each component in the model to a separate topic"""

    def __init__(self, cls: type[M]):
        self._cls = cls
        self._keys = set(self._topic(key) for key in cls.model_fields.keys())
        self._builder = PartialModelBuilder(self._cls)

    def split_to_topics(self, model: M) -> dict[str, str]:
        return {
            self._topic(key): getattr(model, key).model_dump_json(by_alias=True)
            for key in type(model).model_fields.keys()
        }

    def _topic(self, key: str) -> str:
        return hyphenize(key)

    def has(self, topic: str) -> bool:
        return topic in self._keys

    def subscribe_topic(self) -> str:
        return "+"

    def handle_message(self, topic: str, json: str | bytes):
        self._builder.input(topic, json)

    def result(self) -> M | None:
        return self._builder.result()


class DirectMqttMapping[M: ThrsValues](MqttMapping[M]):
    """MQTT mapping that maps the entire model to a single topic"""

    def __init__(self, cls: type[M], topic: str):
        self._cls = cls
        self._topic = topic
        self._value = None

    def split_to_topics(self, model: M) -> dict[str, str]:
        return {self._topic: model.model_dump_json(by_alias=True)}

    def has(self, topic: str) -> bool:
        return topic == self._topic

    def subscribe_topic(self) -> str:
        return self._topic

    def handle_message(self, topic: str, json: str | bytes):
        if topic == self._topic:
            self._value = self._cls.model_validate_json(json)

    def result(self) -> M | None:
        return self._value


class ModuleMqttMapping(MqttMapping[CombinedValues]):
    """MQTT mapping for modules

    Delegates to PartialMqttMapping for each sub-model."""

    def __init__(self, clss: ModuleClassMap):
        self._clss = clss
        self._plain_mappings: Mapping[str, PartialMqttMapping] = {
            name: PartialMqttMapping(module_cls) for name, module_cls in clss.items()
        }
        self._builder = CombinedModelBuilder(self._clss)

    def split_to_topics(self, model: CombinedValues) -> dict[str, str]:
        return {
            f"{hyphenize(module)}/{key}": value
            for module, model in model.values.items()
            for key, value in self._plain_mappings[module]
            .split_to_topics(model)
            .items()
        }

    def has(self, topic: str) -> bool:
        module_name, key, *rest = topic.split("/")
        mapping: PartialMqttMapping | Literal[False] = self._plain_mappings.get(
            module_name, False
        )
        return mapping and mapping.has("/".join([key, *rest]))

    def subscribe_topic(self) -> str:
        return "+/+"

    def handle_message(self, topic: str, json: str | bytes):
        self._builder.input(topic, json)

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
        self._sensor_values_mqtt_mapping = ModuleMqttMapping(sensor_values_clss)
        self._control_values_mqtt_mapping = ModuleMqttMapping(control_values_clss)

        self._running = False

    async def _listen_to_sensors(self):
        async for message in self._mqtt_client.messages:
            topic = self._clean_topic(message.topic)
            if not self._sensor_values_mqtt_mapping.has(topic):
                continue
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            self._sensor_values_mqtt_mapping.handle_message(topic, message.payload)

    async def _publish_by_mapping[T](
        self, client: Client, mapping: MqttMapping[T], value: T
    ):
        payloads = mapping.split_to_topics(value)
        for topic_suffix, payload in payloads.items():
            topic = (
                f"{self._topic_prefix}/{topic_suffix}{self._control_topic_suffix_str}"
            )
            await client.publish(
                topic,
                payload,
                qos=1,
            )

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
        await self._mqtt_client.subscribe(
            f"{self._topic_prefix}/{self._sensor_values_mqtt_mapping.subscribe_topic()}",
            qos=1,
        )

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
        inner: "Simulation",
        mqtt_client: Client,
        topic_prefix: str,
        sensor_values_clss: ModuleClassMap,
        simulation_outputs_cls: type[ThrsValues],
    ):
        self._inner = inner
        self._mqtt_client = mqtt_client
        self._topic_prefix = topic_prefix
        self._sensor_values_mqtt_mapping = ModuleMqttMapping(sensor_values_clss)
        self._simulation_outputs_mqtt_mapping = DirectMqttMapping(
            simulation_outputs_cls, "simulation/outputs"
        )

    async def _publish_by_mapping[T](
        self, client: Client, mapping: MqttMapping[T], value: T
    ):
        payloads = mapping.split_to_topics(value)
        for topic_suffix, payload in payloads.items():
            topic = f"{self._topic_prefix}/{topic_suffix}"
            await client.publish(
                topic,
                payload,
                qos=1,
            )

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
        await self._inner.start()

    async def transceive(
        self, control_values: CombinedValues
    ) -> ExecutionResult[CombinedValues]:
        logging.debug("Executing simulation")
        simulation_result = await self._inner.tick(control_values)
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
        return self._inner.start_time

    def time(self) -> datetime:
        return self._inner.time()


class MqttConnector(Connector[CombinedValues, CombinedValues]):
    # Compatibility wrapper composed from split connectors:
    # - MqttControlConnector handles controller-side MQTT I/O
    # - MqttSimulationConnector handles simulation-side execution and publishing
    def __init__(
        self,
        inner: "Simulation",
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
            inner=inner,
            mqtt_client=environment_client,
            topic_prefix=topic_prefix,
            sensor_values_clss=sensor_values_clss,
            simulation_outputs_cls=simulation_outputs_cls,
        )

    async def start(self):
        await self._control_connector.start()
        await self._simulation_connector.start()

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
