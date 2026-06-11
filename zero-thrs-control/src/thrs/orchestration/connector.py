import logging
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
from thrs.orchestration.module import CombinedModule, MqttMapping
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import IoMapping
from thrs.utils.string import hyphenize

logger = logging.getLogger(__name__)


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
        module_nesting: CombinedModule,
        start_time: datetime | None = None,
    ):
        self._start_time = start_time or datetime.now()
        self._mqtt_client = mqtt_client
        self._topic_prefix = topic_prefix
        self._module_nesting = module_nesting

        self._running = False
        self._sensors_builder = module_nesting.sensor_values_mqtt_mapping.builder()

    async def _listen_to_sensors(self):
        async for message in self._mqtt_client.messages:
            topic = self._clean_topic(message.topic)
            if not self._module_nesting.sensor_values_mqtt_mapping.has(topic):
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
            self._module_nesting.control_values_mqtt_mapping,
            control_values,
        )

    async def start(self):
        await self._mqtt_client.subscribe(
            f"{self._topic_prefix}/{self._module_nesting.sensor_values_mqtt_mapping.subscribe_topic()}",
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
        module_nesting: CombinedModule,
    ):
        self._inner = inner
        self._mqtt_client = mqtt_client
        self._topic_prefix = topic_prefix
        self._module_nesting = module_nesting

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
            self._module_nesting.sensor_values_mqtt_mapping,
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
                self._module_nesting.simulation_output_mqtt_mapping,
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
        module_nesting: CombinedModule,
    ):
        self._control_connector = MqttControlConnector(
            mqtt_client=controller_client,
            topic_prefix=topic_prefix,
            module_nesting=module_nesting,
        )
        self._simulation_connector = MqttSimulationConnector(
            inner=inner,
            mqtt_client=environment_client,
            topic_prefix=topic_prefix,
            module_nesting=module_nesting,
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
