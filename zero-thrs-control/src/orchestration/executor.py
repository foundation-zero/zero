from asyncio import TaskGroup
import asyncio
from datetime import datetime, timedelta

from aiomqtt import Client

from input_output.base import SimulationInputs, ThrsModel
from simulation.io_mapping import IoMapping

from types.executor import ExecutionResult, Executor, SimulationExecutionResult


class MqttExecutor[S: ThrsModel, C: ThrsModel](Executor[S, C]):
    def __init__(
        self,
        inner: Executor,
        controller_client: Client,
        world_client: Client,
        sensor_topic: str,
        sensor_cls: type[S],
        control_topic: str,
        control_cls: type[C],
    ):
        self._inner = inner
        self._controller_client = controller_client
        self._world_client = world_client
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
        async for message in self._world_client.messages:
            if not isinstance(message.payload, str | bytes):
                raise ValueError(
                    f"Expected string or bytes, got {type(message.payload)}"
                )
            self._last_controls = self._control_cls.model_validate_json(message.payload)
            execution_result = await self._inner.tick(self._last_controls)
            await self._world_client.publish(
                self._sensor_topic,
                execution_result.sensor_values.model_dump_json(),
                qos=1,
            )

    async def start(self):
        await self._controller_client.subscribe(self._sensor_topic, qos=1)
        await self._world_client.subscribe(self._control_topic, qos=1)
        async with TaskGroup() as tg:
            tg.create_task(self._listen_to_sensors())
            tg.create_task(self._pass_controls_to_inner())

    async def tick(self, control_values: ThrsModel) -> ExecutionResult[S]:
        await self._world_client.publish(
            self._control_topic, control_values.model_dump_json(), qos=1
        )
        return await self._sensors.get()


class SimulationExecutor(Executor):
    def __init__(
        self,
        io_mapping: IoMapping,
        boundaries: SimulationInputs,
        start_time: datetime,
        tick_duration: timedelta,
    ):
        self._start_time = start_time
        self._ticks = 0
        self._tick_duration = tick_duration
        self._boundaries = boundaries
        self._io_mapping = io_mapping

    async def tick(self, control_values: ThrsModel) -> ExecutionResult:
        time = self._start_time + self._ticks * self._tick_duration
        bounds = self._boundaries.get_values_at_time(time)
        sensor_values, simulation_outputs, raw = self._io_mapping.tick(
            control_values, bounds, time, self._tick_duration
        )
        return SimulationExecutionResult(
            timestamp=time,
            sensor_values=sensor_values,
            simulation_outputs=simulation_outputs,
            raw=raw,
        )
