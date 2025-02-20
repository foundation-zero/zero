from aiomqtt import Client

from zero_domestic_control.messages import Blind, LightingGroup, Room

rooms_topic = "domestic/rooms"
lighting_groups_topic = "domestic/lighting_groups"
blinds_topic = "domestic/blinds"


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
