from typing import Optional
from aiomqtt import Client
from pydantic import BaseModel

rooms_topic = "domestic/rooms"
lighting_groups_topic = "domestic/lighting_groups"
blinds_topic = "domestic/blinds"


class Room(BaseModel):
    id: str
    actual_temperature: Optional[float]
    temperature_setpoint: Optional[float]
    actual_humidity: Optional[float]
    amplifier_on: Optional[bool]


class Blind(BaseModel):
    id: str
    level: float


class LightingGroup(BaseModel):
    id: str
    level: float


class Mqtt:
    def __init__(self, mqtt: Client):
        self._mqtt = mqtt

    async def send_room(self, room: Room):
        payload = room.model_dump_json(exclude_none=True)
        await self._mqtt.publish(rooms_topic, payload, qos=1)

    async def send_blind(self, blind: Blind):
        payload = blind.model_dump_json(exclude_none=True)
        await self._mqtt.publish(blinds_topic, payload, qos=1)

    async def send_lighting_group(self, lighting_group: LightingGroup):
        payload = lighting_group.model_dump_json(exclude_none=True)
        await self._mqtt.publish(lighting_groups_topic, payload, qos=1)
