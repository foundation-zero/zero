from typing import ClassVar
from zero_domestic_control.messages import Message
from aiomqtt import Client as MqttClient

from zero_domestic_control.mqtt import send_message


class RoomTemperatureSetpoint(Message):
    TOPIC: ClassVar[str] = "thrs/room-temperature-setpoint/:id"

    id: str
    temperature: float


class RoomHumiditySetpoint(Message):
    TOPIC: ClassVar[str] = "thrs/room-humidity-setpoint/:id"

    id: str
    humidity: float


class RoomCo2Setpoint(Message):
    TOPIC: ClassVar[str] = "thrs/room-co2-setpoint/:id"

    id: str
    co2: float


class Thrs:
    def __init__(self, mqtt_client: MqttClient):
        self._mqtt = mqtt_client

    async def set_room_temperature_setpoint(self, room: str, temperature: float):
        await send_message(
            self._mqtt, RoomTemperatureSetpoint(id=room, temperature=temperature)
        )

    async def set_room_humidity_setpoint(self, room: str, humidity: float):
        await send_message(self._mqtt, RoomHumiditySetpoint(id=room, humidity=humidity))

    async def set_room_co2_setpoint(self, room: str, co2: float):
        await send_message(self._mqtt, RoomCo2Setpoint(id=room, co2=co2))
