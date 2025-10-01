from asyncio import Future
from typing import Coroutine
from aiomqtt import Client as MqttClient, Message

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
        self._first_sensor_values = Future()
        self._first_control_values = Future()

    async def run(self) -> Coroutine[None, None, None]:
        await self._mqtt_client.subscribe("thrs/sensor_values", qos=1)
        await self._mqtt_client.subscribe("thrs/control_values", qos=1)

        async def _run(self):
            async for message in self._mqtt_client.messages:
                if message.topic.matches("thrs/sensor_values"):
                    self._sensor_values = self._parse_message(
                        message, self._sensor_values_cls
                    )
                    if not self._first_sensor_values.done():
                        self._first_sensor_values.set_result(self._sensor_values)
                elif message.topic.matches("thrs/control_values"):
                    self._control_values = self._parse_message(
                        message, self._control_values_cls
                    )
                    if not self._first_control_values.done():
                        self._first_control_values.set_result(self._control_values)

        return _run(self)

    async def wait_for_values(self):
        return await self._first_sensor_values, await self._first_control_values

    async def send_manual_controls(self, control_values: ThrustersControlValues):
        await self._mqtt_client.publish(
            "thrs/manual_controls", control_values.model_dump_json(), qos=1
        )

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
