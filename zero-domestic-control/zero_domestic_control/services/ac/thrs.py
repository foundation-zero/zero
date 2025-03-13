from typing import ClassVar
from zero_domestic_control.messages import Message
from aiomqtt import Client as MqttClient

from zero_domestic_control.mqtt import send_message


class RoomTemperatureSetpoint(Message):
    TOPIC: ClassVar[str] = "thrs/room-temperature-setpoint/:id"

    id: str
    temperature: float


class Thrs:
    def __init__(self, mqtt_client: MqttClient):
        self._mqtt = mqtt_client

    async def set_room_temperature_setpoint(self, room: str, temperature: float):
        await send_message(
            self._mqtt, RoomTemperatureSetpoint(id=room, temperature=temperature)
        )
