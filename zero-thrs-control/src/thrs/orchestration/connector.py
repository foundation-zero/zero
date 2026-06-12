import logging
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal, Protocol

from aiomqtt import Client, Topic

from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.input_output.model_builder import (
    CombinedModelBuilder,
    ModelBuilder,
    PartialModelBuilder,
)
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import IoMapping
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)


class MqttMapping[M](Protocol):
    """Mapping between a model and MQTT topics"""

    def split_to_topics(self, model: M) -> dict[str, str]: ...

    def builder(self) -> ModelBuilder[M]: ...

    def has(self, topic: str) -> bool: ...

    def subscribe_topic(self) -> str: ...


class PartialMqttMapping[M: ThrsValues](MqttMapping[M]):
    """MQTT mapping that maps each component in the model to a separate topic"""

    def __init__(self, cls: type[M], topic_suffix: str | None = None):
        self._cls = cls
        self._topic_suffix = topic_suffix
        self._keys = set(self._topic(key) for key in cls.model_fields.keys())

    def split_to_topics(self, model: M) -> dict[str, str]:
        return {
            self._topic(key): getattr(model, key).model_dump_json(by_alias=True)
            for key in type(model).model_fields.keys()
        }

    def _topic(self, key: str) -> str:
        return (
            f"{hyphenize(key)}/{self._topic_suffix}"
            if self._topic_suffix
            else hyphenize(key)
        )

    def has(self, topic: str) -> bool:
        return topic in self._keys

    def subscribe_topic(self) -> str:
        return f"+/{self._topic_suffix}" if self._topic_suffix else "+"

    def builder(self) -> ModelBuilder[M]:
        return PartialModelBuilder(self._cls)


class DirectMqttMapping[M: ThrsValues](MqttMapping[M]):
    """MQTT mapping that maps the entire model to a single topic

    Currently doesn't support builder"""

    def __init__(self, cls: type[M], topic: str):
        self._cls = cls
        self._topic = topic

    def split_to_topics(self, model: M) -> dict[str, str]:
        return {self._topic: model.model_dump_json(by_alias=True)}

    def has(self, topic: str) -> bool:
        return topic == self._topic

    def subscribe_topic(self) -> str:
        return self._topic

    def builder(self) -> ModelBuilder[M]:
        raise NotImplementedError()


class ModuleMqttMapping(MqttMapping[CombinedValues]):
    """MQTT mapping for modules

    Delegates to PartialMqttMapping for each sub-model."""

    def __init__(
        self, clss: Mapping[str, type[ThrsValues]], topic_suffix: str | None = None
    ):
        self._clss = dict(clss)
        self._plain_mappings: dict[str, PartialMqttMapping] = {
            name: PartialMqttMapping(cls, topic_suffix)
            for name, cls in self._clss.items()
        }
        self._topic_suffix = topic_suffix

    def split_to_topics(self, model: CombinedValues) -> dict[str, str]:
        return {
            f"{hyphenize(module)}/{key}": value
            for module, model in model.values.items()
            for key, value in self._plain_mappings[module]
            .split_to_topics(model)
            .items()
        }

    def builder(self) -> ModelBuilder[CombinedValues]:
        return CombinedModelBuilder(self._clss)

    def has(self, topic: str) -> bool:
        module_name, key, *rest = topic.split("/")
        mapping: PartialMqttMapping | Literal[False] = self._plain_mappings.get(
            module_name, False
        )
        return mapping and mapping.has("/".join([key, *rest]))

    def subscribe_topic(self) -> str:
        return f"+/+/{self._topic_suffix}" if self._topic_suffix else "+/+"


@dataclass
class ExecutionResult[S]:
    timestamp: datetime
    sensor_values: S


class Connector[S, C](Protocol):
    async def start(self): ...
    async def tick(self, control_values: C) -> ExecutionResult[S]: ...

    @property
    def start_time(self) -> datetime: ...

    def time(self) -> datetime: ...


class MqttControlConnector(Connector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        mqtt_client: Client,
        topic_prefix: str,
        sensor_values_mqtt_mapping: MqttMapping,
        control_values_mqtt_mapping: MqttMapping,
        start_time: datetime | None = None,
    ):
        self._start_time = start_time or datetime.now()
        self._mqtt_client = mqtt_client
        self._topic_prefix = topic_prefix
        self._sensor_values_mqtt_mapping = sensor_values_mqtt_mapping
        self._control_values_mqtt_mapping = control_values_mqtt_mapping

        self._running = False
        self._sensors_builder = self._sensor_values_mqtt_mapping.builder()

    async def _listen_to_sensors(self):
        async for message in self._mqtt_client.messages:
            topic = self._clean_topic(message.topic)
            if not self._sensor_values_mqtt_mapping.has(topic):
                continue
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            self._sensors_builder.input(topic, message.payload)

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

    async def tick(
        self, control_values: CombinedValues
    ) -> ExecutionResult[CombinedValues]:
        if not self._running:
            raise Exception(
                "MqttControlConnector not running, run() should be called in a create_task()"
            )
        sensors = self._sensors_builder.result()
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
        sensor_values_mqtt_mapping: MqttMapping,
        simulation_outputs_mqtt_mapping: MqttMapping,
    ):
        self._inner = inner
        self._mqtt_client = mqtt_client
        self._topic_prefix = topic_prefix
        self._sensor_values_mqtt_mapping = sensor_values_mqtt_mapping
        self._simulation_outputs_mqtt_mapping = simulation_outputs_mqtt_mapping

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

    async def tick(
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
        sensor_values_mqtt_mapping: MqttMapping,
        control_values_mqtt_mapping: MqttMapping,
        simulation_outputs_mqtt_mapping: MqttMapping,
    ):
        self._control_connector = MqttControlConnector(
            mqtt_client=controller_client,
            topic_prefix=topic_prefix,
            sensor_values_mqtt_mapping=sensor_values_mqtt_mapping,
            control_values_mqtt_mapping=control_values_mqtt_mapping,
        )
        self._simulation_connector = MqttSimulationConnector(
            inner=inner,
            mqtt_client=environment_client,
            topic_prefix=topic_prefix,
            sensor_values_mqtt_mapping=sensor_values_mqtt_mapping,
            simulation_outputs_mqtt_mapping=simulation_outputs_mqtt_mapping,
        )

    async def start(self):
        await self._control_connector.start()
        await self._simulation_connector.start()

    async def run(self):
        await self._control_connector.run()

    async def tick(
        self, control_values: CombinedValues
    ) -> ExecutionResult[CombinedValues]:
        await self._control_connector.tick(control_values)
        return await self._simulation_connector.tick(control_values)

    @property
    def start_time(self) -> datetime:
        return self._simulation_connector.start_time

    def time(self) -> datetime:
        return self._simulation_connector.time()


# TODO: Move below classes to another file
@dataclass
class SimulationResult[
    S,
    C,
    I: SimulationInputs,
    O: SimulationValues,
](ExecutionResult[S]):
    control_values: C
    simulation_outputs: O
    simulation_inputs: I
    raw: dict[str, Any]
    fmu: Fmu

    def read_fmu_value(self, name: str) -> Any:
        variable = next(
            (
                variable
                for variable in self.fmu._model_description.modelVariables
                if name == variable.name
            ),
            None,
        )
        if variable is None:
            raise ValueError(f"Variable '{name}' not found in FMU model.")
        return self.fmu._fmu_instance.getReal([variable.valueReference])[0]  # type: ignore

    def find_fmu_variables(
        self, name: str, match: Literal["include", "startswith"] = "include"
    ) -> list[Any]:
        return [
            variable
            for variable in self.fmu._model_description.modelVariables
            if (
                name in variable.name
                if match == "include"
                else variable.name.startswith(name)
            )
        ]

    def summarize_fmu_values(self, name: str) -> dict[str, Any]:
        variables = self.find_fmu_variables(f"{name}.summary", match="startswith")
        return {
            variable.name: self.read_fmu_value(variable.name) for variable in variables
        }


class Simulation[
    S,
    C,
    I: SimulationInputs,
    O: SimulationValues,
]:
    def __init__(
        self,
        io_mapping: IoMapping[S, C, I, O],
        fmu: Fmu,
        simulation_inputs: I,
        start_time: datetime,
        tick_duration: timedelta,
    ):
        self._start_time = start_time
        self._ticks = 0
        self._tick_duration = tick_duration
        self._simulation_inputs = simulation_inputs
        self._fmu = fmu
        self._io_mapping = io_mapping

    async def start(self):
        pass

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def tick_duration(self) -> timedelta:
        return self._tick_duration

    def time(self):
        return self._start_time + self._ticks * self._tick_duration

    async def tick(self, control_values: C) -> SimulationResult[S, C, I, O]:
        logging.debug("Running simulation tick")
        time = self.time()

        simulation_inputs = self._simulation_inputs.get_values_at_time(time)
        fmu_inputs = self._io_mapping.generate_inputs(control_values, simulation_inputs)
        fmu_outputs = self._fmu.tick(fmu_inputs, self._tick_duration)
        sensor_values, simulation_outputs, raw = self._io_mapping.construct_outputs(
            fmu_inputs, fmu_outputs, simulation_inputs, time + self._tick_duration
        )

        self._ticks += 1
        return SimulationResult(
            timestamp=time,
            sensor_values=sensor_values,
            control_values=control_values,
            simulation_outputs=simulation_outputs,
            simulation_inputs=simulation_inputs,
            raw=raw,
            fmu=self._fmu,
        )

    def update_simulation_inputs(self, simulation_inputs: I):
        self._simulation_inputs = simulation_inputs
