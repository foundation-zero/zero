from asyncio import TaskGroup
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal

from aiomqtt import Client

from input_output.base import SimulationInputs, ThrsModel
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping

from classes.executor import ExecutionResult, Executor


class MqttExecutor[S: ThrsModel, C: ThrsModel](Executor[S, C]):
    def __init__(
        self,
        inner: Executor,
        controller_client: Client,
        environment_client: Client,
        sensor_topic: str,
        sensor_cls: type[S],
        control_topic: str,
        control_cls: type[C],
    ):
        self._inner = inner
        self._controller_client = controller_client
        self._environment_client = environment_client
        self._sensor_topic = sensor_topic
        self._control_topic = control_topic
        self._sensors: asyncio.Queue[ExecutionResult[S]] = asyncio.Queue()
        self._sensor_cls = sensor_cls
        self._last_controls = None
        self._control_cls = control_cls

    async def _listen_to_sensors(self):
        async for message in self._controller_client.messages:
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            sensors = self._sensor_cls.model_validate_json(message.payload)
            await self._sensors.put(
                ExecutionResult(timestamp=datetime.now(), sensor_values=sensors)
            )

    async def _pass_controls_to_inner(self):
        async for message in self._environment_client.messages:
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            self._last_controls = self._control_cls.model_validate_json(message.payload)
            execution_result = await self._inner.tick(self._last_controls)
            await self._environment_client.publish(
                self._sensor_topic,
                execution_result.sensor_values.model_dump_json(),
                qos=1,
            )

    async def start(self):
        await self._controller_client.subscribe(self._sensor_topic, qos=1)
        await self._environment_client.subscribe(self._control_topic, qos=1)

    async def run(self):
        async with TaskGroup() as tg:
            tg.create_task(self._listen_to_sensors())
            tg.create_task(self._pass_controls_to_inner())

    async def tick(self, control_values: ThrsModel) -> ExecutionResult[S]:
        await self._environment_client.publish(
            self._control_topic, control_values.model_dump_json(), qos=1
        )
        return await self._sensors.get()

    @property
    def start_time(self) -> datetime:
        return self._inner.start_time

@dataclass
class SimulationExecutionResult[S: ThrsModel, I: SimulationInputs, O: ThrsModel](
    ExecutionResult[S]
):
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


class SimulationExecutor[S: ThrsModel, C: ThrsModel, I: SimulationInputs, O: ThrsModel](
    Executor[S, C]
):
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

    async def tick(self, control_values: C) -> SimulationExecutionResult[S, I, O]:
        time = self.time()
        simulation_inputs = self._simulation_inputs.get_values_at_time(time)
        sensor_values, simulation_outputs, raw = self._io_mapping.tick(
            control_values, simulation_inputs, time, self._tick_duration
        )
        self._ticks += 1
        return SimulationExecutionResult(
            timestamp=time,
            sensor_values=sensor_values,
            simulation_outputs=simulation_outputs,
            simulation_inputs=simulation_inputs,
            raw=raw,
            fmu=self._io_mapping._fmu,
        )
