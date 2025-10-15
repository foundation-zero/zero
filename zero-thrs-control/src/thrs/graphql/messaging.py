from asyncio import Queue
import asyncio
from typing import Coroutine, Literal
from aiomqtt import Client as MqttClient, Message

from thrs.cli.simulation_controls import PlayMessage, StatusMessage, StepMessage
from thrs.input_output.base import ThrsModel
from thrs.input_output.modules.thrusters import ThrustersControlValues


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
        self._sensor_values = None
        self._control_values = None
        self._simulation_status = None
        self._waiting_for_status = False
        self._status_msgs = Queue[StatusMessage]()

    async def run(self) -> Coroutine[None, None, None]:
        await self._mqtt_client.subscribe("thrs/sensor_values", qos=1)
        await self._mqtt_client.subscribe("thrs/control_values", qos=1)
        await self._mqtt_client.subscribe("thrs/simulation/status", qos=1)

        async def _run(self):
            async for message in self._mqtt_client.messages:
                if message.topic.matches("thrs/sensor_values"):
                    self._sensor_values = self._parse_message(
                        message, self._sensor_values_cls
                    )

                elif message.topic.matches("thrs/control_values"):
                    self._control_values = self._parse_message(
                        message, self._control_values_cls
                    )
                elif message.topic.matches("thrs/simulation/status"):
                    self._simulation_status = self._parse_message(
                        message, StatusMessage
                    )
                    if self._waiting_for_status:
                        await self._status_msgs.put(self._simulation_status)

        return _run(self)

    async def send_manual_controls(self, control_values: ThrustersControlValues):
        await self._mqtt_client.publish(
            "thrs/manual_controls", control_values.model_dump_json(), qos=1
        )

    async def play_simulation(self, playback_rate: float):
        await self._mqtt_client.publish(
            "thrs/simulation/play",
            PlayMessage(playback_rate=playback_rate).model_dump_json(),
            qos=1,
        )

    async def pause_simulation(self):
        await self._mqtt_client.publish("thrs/simulation/pause", "", qos=1)

    async def step_simulation(self, seconds: float):
        await self._mqtt_client.publish(
            "thrs/simulation/step",
            StepMessage(seconds=seconds).model_dump_json(),
            qos=1,
        )

    async def wait_for_status(
        self, status: Literal["stepping", "running", "available"], timeout: float
    ) -> StatusMessage:
        async with asyncio.timeout(timeout):
            self._waiting_for_status = True
            try:
                while True:
                    msg = await self._status_msgs.get()
                    if msg.status == status:
                        return msg
            finally:
                self._waiting_for_status = False

    def _parse_message[T: ThrsModel](self, message: Message, model: type[T]) -> T:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        return model.model_validate_json(message.payload)

    @property
    def sensor_values(self) -> SensorValues | None:
        return self._sensor_values

    @property
    def control_values(self) -> ControlValues | None:
        return self._control_values

    @property
    def simulation_status(self) -> StatusMessage | None:
        return self._simulation_status
