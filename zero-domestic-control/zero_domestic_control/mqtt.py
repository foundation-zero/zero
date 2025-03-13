from typing import AsyncIterable
from aiomqtt import Client, Message as MqttMessage

from zero_domestic_control.messages import (
    Blind,
    LightingGroup,
    Message,
    Room,
    RoomTemperatureSetpoint,
)


async def send_message(mqtt: Client, message: Message):
    exclude = {"id"} if ":id" in message.TOPIC else set()
    payload = message.model_dump_json(exclude_none=True, exclude=exclude)
    topic = message.TOPIC.replace(":id", message.id)
    await mqtt.publish(topic, payload, qos=1)


class DataCollection:
    """MQTT interface for data collection"""

    def __init__(self, mqtt: Client):
        self._mqtt = mqtt

    async def send_room(self, room: Room):
        await send_message(self._mqtt, room)

    async def send_blind(self, blind: Blind):
        await send_message(self._mqtt, blind)

    async def send_lighting_group(self, lighting_group: LightingGroup):
        await send_message(self._mqtt, lighting_group)


class ControlSend:
    """The sender of commands to the control system"""

    def __init__(self, mqtt: Client):
        self._mqtt = mqtt

    async def send_room_setpoint(self, room: str, temperature: float):
        await send_message(
            self._mqtt, RoomTemperatureSetpoint(id=room, temperature=temperature)
        )


type ControlMessages = RoomTemperatureSetpoint
_CONTROL_LISTEN_MESSAGE = [RoomTemperatureSetpoint]


class ControlReceive:
    """The receiver of commands sent to the control system"""

    def __init__(self, mqtt: Client):
        self._mqtt = mqtt

    async def listen(self):
        for topic in _CONTROL_LISTEN_MESSAGE:
            print(f"listening to {topic.wildcard().value}")
            await self._mqtt.subscribe(topic.wildcard().value, qos=1)

    def _parse_message(self, message: MqttMessage) -> ControlMessages | None:
        for cls in _CONTROL_LISTEN_MESSAGE:
            if message.topic.matches(cls.wildcard()):
                if not isinstance(message.payload, str | bytes):
                    raise ValueError(f"invalid message {message.topic.value}")
                context = {"id": id} if (id := cls.extract_id(message.topic)) else {}
                return cls.model_validate_json(message.payload, context=context)
        return None

    @property
    async def messages(self) -> AsyncIterable[ControlMessages]:
        async for message in self._mqtt.messages:
            if control_msg := self._parse_message(message):
                yield control_msg
