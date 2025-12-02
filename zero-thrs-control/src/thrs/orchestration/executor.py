from asyncio import TaskGroup
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any, Literal

from aiomqtt import Client, Topic

from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsModel
from thrs.input_output.model_builder import ModelBuilder
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import IoMapping

from thrs.classes.executor import ExecutionResult, Executor
from thrs.utils.string import dash_to_snake, hyphenize

logger = logging.getLogger(__name__)


class MqttExecutor[S: ThrsModel, C: ThrsModel, O: SimulationValues](Executor[S, C]):
    # Controller client listens to sensor values and publishes control values (our control logic)
    # Environment client listens to control values and publishes sensor values (mimicking the PLC)
    def __init__(
        self,
        inner: Executor,
        controller_client: Client,
        environment_client: Client,
        topic_prefix: str,
        sensor_cls: type[S],
        control_topic_suffix: str,
        control_cls: type[C],
        simulation_output: tuple[str, type[O]] | None = None,
    ):
        self._inner = inner
        self._controller_client = controller_client
        self._environment_client = environment_client
        self._topic_prefix = topic_prefix
        self._control_topic_suffix = control_topic_suffix
        self._sensor_cls = sensor_cls

        self._running = False
        self._sensors_builder = ModelBuilder(sensor_cls)
        self._controls_builder = ModelBuilder(control_cls)
        self._triggers: asyncio.Queue[None] = asyncio.Queue()

        self._simulation_output_topic, self._simulation_output_cls = (
            simulation_output if simulation_output else (None, None)
        )

    async def _listen_to_sensors(self):
        async for message in self._controller_client.messages:
            if message.topic.value.endswith(f"/{self._control_topic_suffix}"):
                continue
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            key = self._extract_key_from_topic(message.topic)
            self._sensors_builder.input(key, message.payload)

    async def _listen_to_controls(self):
        async for message in self._environment_client.messages:
            if not message.topic.value.endswith(f"/{self._control_topic_suffix}"):
                continue
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            key = self._extract_key_from_topic(message.topic)
            self._controls_builder.input(key, message.payload)

    async def _pass_controls_to_inner(self):
        while True:
            logging.debug("Received trigger, passing to inner executor")
            await self._triggers.get()
            control_values = self._controls_builder.result()
            if control_values is None:
                control_values = await self._controls_builder.wait_for_result()

            execution_result = await self._inner.tick(control_values)
            await self._send_sensor_values(execution_result)
            if (
                isinstance(execution_result, SimulationExecutionResult)
                and self._simulation_output_topic
                and self._simulation_output_cls
            ):
                logging.debug("Publishing simulation output values")
                await self._environment_client.publish(
                    self._simulation_output_topic,
                    execution_result.simulation_outputs.model_dump_json(),
                    qos=1,
                )

    def _extract_key_from_topic(self, topic: Topic) -> str:
        key, *_rest = topic.value.removeprefix(f"{self._topic_prefix}/").split("/")
        return dash_to_snake(
            key
        )  # TODO: figure out if we want the fields in the module to be aliased and then look those up

    async def _send_model(
        self, client: Client, model: ThrsModel, topic_suffix: str | None = None
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

    async def _send_sensor_values(self, execution_result: ExecutionResult[S]):
        logging.debug("Publishing sensor values")
        await self._send_model(self._environment_client, execution_result.sensor_values)

    async def _send_control_values(self, control_values: C):
        logging.debug("Publishing control values")
        await self._send_model(
            self._controller_client, control_values, self._control_topic_suffix
        )

    async def start(self):
        await self._controller_client.subscribe(f"{self._topic_prefix}/#", qos=1)
        await self._environment_client.subscribe(f"{self._topic_prefix}/#", qos=1)

    async def run(self):
        self._running = True
        try:
            async with TaskGroup() as tg:
                tg.create_task(self._listen_to_sensors())
                tg.create_task(self._listen_to_controls())
                tg.create_task(self._pass_controls_to_inner())
        except Exception as e:
            logger.error(f"MqttExecutor run encountered an error: {e}")
        finally:
            self._running = False

    async def tick(self, control_values: C) -> ExecutionResult[S]:
        if not self._running:
            raise Exception(
                "MqttExecutor not running, run() should be called in a create_task()"
            )
        sensors = self._sensors_builder.result()
        await self._send_control_values(control_values)

        self._triggers.put_nowait(None)

        return ExecutionResult(
            timestamp=datetime.now(),
            sensor_values=sensors if sensors else self._sensor_cls.zero(),
        )

    @property
    def start_time(self) -> datetime:
        return self._inner.start_time

    def time(self) -> datetime:
        return self._inner.time()


@dataclass
class SimulationExecutionResult[
    S: ThrsModel,
    C: ThrsModel,
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


class SimulationExecutor[
    S: ThrsModel,
    C: ThrsModel,
    I: SimulationInputs,
    O: SimulationValues,
](Executor[S, C]):
    def __init__(
        self,
        io_mapping: IoMapping[S, C, I, O],
        simulation_inputs: I,
        start_time: datetime,
        tick_duration: timedelta,
    ):
        self._start_time = start_time
        self._ticks = 0
        self._tick_duration = tick_duration
        self._simulation_inputs = simulation_inputs
        self._io_mapping = io_mapping

    async def start(self):
        pass

    @property
    def start_time(self) -> datetime:
        return self._start_time

    def time(self):
        return self._start_time + self._ticks * self._tick_duration

    async def tick(self, control_values: C) -> SimulationExecutionResult[S, C, I, O]:
        logging.debug("Running simulation tick")
        time = self.time()
        simulation_inputs = self._simulation_inputs.get_values_at_time(time)
        sensor_values, simulation_outputs, raw = self._io_mapping.tick(
            control_values, simulation_inputs, time, self._tick_duration
        )
        self._ticks += 1
        return SimulationExecutionResult(
            timestamp=time,
            sensor_values=sensor_values,
            control_values=control_values,
            simulation_outputs=simulation_outputs,
            simulation_inputs=simulation_inputs,
            raw=raw,
            fmu=self._io_mapping._fmu,
        )

    def update_simulation_inputs(self, simulation_inputs: I):
        self._simulation_inputs = simulation_inputs
