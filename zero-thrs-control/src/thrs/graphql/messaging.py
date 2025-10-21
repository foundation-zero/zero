from asyncio import Queue
import asyncio
from typing import Callable, Coroutine, Literal
from aiomqtt import Client as MqttClient, Message

from thrs.cli.simulation_controls import (
    ControlStatusMessage,
    ManualControlMessage,
    PauseMessage,
    PlayMessage,
    SimulationStatusMessage,
    StepMessage,
    SetAutomationMessage,
)
from thrs.input_output.base import ThrsModel
from thrs.input_output.modules.thrusters import ThrustersControlValues


class MessageReceiver[T: ThrsModel]:
    def __init__(self, cls: type[T], topic: str):
        self._cls = cls
        self._last: T | None = None
        self._waiting = False
        self._msgs = Queue[T]()
        self._topic = topic

    @property
    def last(self) -> T | None:
        return self._last

    async def wait_for(self, condition: Callable[[T], bool], timeout: float) -> T:
        async with asyncio.timeout(timeout):
            self._waiting = True
            try:
                while True:
                    msg = await self._msgs.get()
                    if condition(msg):
                        return msg
            finally:
                self._waiting = False

    async def handle(self, msg: T):
        self._last = msg
        if self._waiting:
            await self._msgs.put(msg)

    @property
    def cls(self):
        return self._cls

    @property
    def topic(self):
        return self._topic


class Messaging[SensorValues: ThrsModel, ControlValues: ThrsModel]:
    def __init__(
        self,
        mqtt_client: MqttClient,
        sensor_values_cls: type[SensorValues],
        control_values_cls: type[ControlValues],
    ):
        self._mqtt_client = mqtt_client
        self._sensor_values_cls = sensor_values_cls
        self._control_values_cls = control_values_cls
        self._sensor_values = MessageReceiver(sensor_values_cls, "thrs/sensor_values")
        self._control_values = MessageReceiver(
            control_values_cls, "thrs/control_values"
        )
        self._simulation_status = MessageReceiver(
            SimulationStatusMessage, SimulationStatusMessage.topic()
        )
        self._control_status = MessageReceiver(
            ControlStatusMessage, ControlStatusMessage.topic()
        )

    @property
    def _statuses(self):
        return [
            self._sensor_values,
            self._control_values,
            self._simulation_status,
            self._control_status,
        ]

    async def run(self) -> Coroutine[None, None, None]:
        for status in self._statuses:
            await self._mqtt_client.subscribe(status.topic, qos=1)

        async def _run(self):
            async for message in self._mqtt_client.messages:
                if status := self.match_receiver(message):
                    await status.handle(self._parse_message(message, status.cls))

        return _run(self)

    def match_receiver(self, message: Message) -> MessageReceiver | None:
        for status in self._statuses:
            if message.topic.matches(status.topic):
                return status
        return None

    async def send_manual_controls(self, control_values: ThrustersControlValues):
        await self._mqtt_client.publish(
            ManualControlMessage.topic(),
            ManualControlMessage(control_values=control_values).model_dump_json(),
            qos=1,
        )

    async def play_simulation(self, playback_rate: float):
        await self._mqtt_client.publish(
            PlayMessage.topic(),
            PlayMessage(playback_rate=playback_rate).model_dump_json(),
            qos=1,
        )

    async def pause_simulation(self):
        await self._mqtt_client.publish(
            PauseMessage.topic(), PauseMessage().model_dump_json(), qos=1
        )

    async def step_simulation(self, seconds: float):
        await self._mqtt_client.publish(
            StepMessage.topic(),
            StepMessage(seconds=seconds).model_dump_json(),
            qos=1,
        )

    async def set_automation(self, enabled: bool):
        await self._mqtt_client.publish(
            SetAutomationMessage.topic(),
            SetAutomationMessage(enabled=enabled).model_dump_json(),
            qos=1,
        )

    async def wait_for_simulation_status(
        self,
        status: Literal["stepping", "running", "available"],
        *_args,
        timeout: float,
    ) -> SimulationStatusMessage:
        return await self._simulation_status.wait_for(
            lambda s: s.status == status, timeout
        )

    async def wait_for_control_status(
        self, automatic: bool, *_args, timeout: float
    ) -> ControlStatusMessage:
        return await self._control_status.wait_for(
            lambda s: s.automatic == automatic, timeout
        )

    async def wait_for_control_values(
        self, condition: Callable[[ControlValues], bool], *_args, timeout: float
    ) -> ControlValues:
        return await self._control_values.wait_for(condition, timeout)

    def _parse_message[T: ThrsModel](self, message: Message, model: type[T]) -> T:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        return model.model_validate_json(message.payload)

    @property
    def sensor_values(self) -> SensorValues | None:
        return self._sensor_values.last

    @property
    def control_values(self) -> ControlValues | None:
        return self._control_values.last

    @property
    def simulation_status(self) -> SimulationStatusMessage | None:
        return self._simulation_status.last

    @property
    def control_status(self) -> ControlStatusMessage | None:
        return self._control_status.last
