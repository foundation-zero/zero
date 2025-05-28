from typing import ClassVar, Optional
from aiomqtt import Topic, Wildcard
from pydantic import BaseModel, model_validator


class Message(BaseModel):
    TOPIC: ClassVar[str]
    id: str

    @classmethod
    def wildcard(cls) -> Wildcard:
        return Wildcard(cls.TOPIC.replace(":id", "#"))

    @classmethod
    def extract_id(cls, topic: Topic) -> str | None:
        if ":id" in cls.TOPIC:
            without_id = cls.TOPIC.replace(":id", "", count=1)
            return topic.value.replace(without_id, "", count=1)
        return None

    @model_validator(mode="before")
    @classmethod
    def _id_from_context(cls, values, info):
        if "id" not in values and isinstance(info.context, dict):
            values["id"] = info.context.get("id")
        return values


class Room(Message):
    TOPIC: ClassVar[str] = "domestic/rooms"
    actual_temperature: Optional[float]
    temperature_setpoint: Optional[float]
    actual_humidity: Optional[float]
    humidity_setpoint: Optional[float]
    actual_co2: Optional[float]
    co2_setpoint: Optional[float]
    amplifier_on: Optional[bool]


class Blind(Message):
    TOPIC: ClassVar[str] = "domestic/blinds"
    level: float


class LightingGroup(Message):
    TOPIC: ClassVar[str] = "domestic/lighting-groups"
    level: float


class RoomTemperatureSetpoint(Message):
    TOPIC: ClassVar[str] = "domestic/control/room-temperature-setpoint/:id"
    temperature: float


class RoomHumiditySetpoint(Message):
    TOPIC: ClassVar[str] = "domestic/control/room-humidity-setpoint/:id"
    humidity: float


class RoomCo2Setpoint(Message):
    TOPIC: ClassVar[str] = "domestic/control/room-co2-setpoint/:id"
    co2: float
