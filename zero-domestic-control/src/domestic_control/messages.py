from typing import ClassVar, Annotated
from aiomqtt import Topic, Wildcard
from pydantic import BaseModel, model_validator
from sqlmodel import SQLModel, Field


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


class Model(SQLModel, Message):
    __table_args__ = {"schema": "domestic"}


class AirConditioning(Model, table=True):
    __tablename__ = "air_conditioning"  # type: ignore
    TOPIC: ClassVar[str] = "domestic/ac"
    id: Annotated[str, Field(primary_key=True)]
    actual_temperature: float | None
    temperature_setpoint: float | None
    actual_humidity: float | None
    humidity_setpoint: float | None


class Amplifier(Model, table=True):
    __tablename__ = "amplifiers"  # type: ignore

    TOPIC: ClassVar[str] = "domestic/amplifiers"
    id: Annotated[str, Field(primary_key=True)]
    on: bool


class Blind(Model, table=True):
    __tablename__ = "blinds"  # type: ignore
    TOPIC: ClassVar[str] = "domestic/blinds"
    id: Annotated[str, Field(primary_key=True)]
    room_id: str
    level: Annotated[float, Field(ge=0, le=1)]


class LightingGroup(Model, table=True):
    __tablename__ = "lighting_groups"  # type: ignore
    TOPIC: ClassVar[str] = "domestic/lighting-groups"
    id: Annotated[str, Field(primary_key=True)]
    room_id: str
    level: Annotated[float, Field(ge=0, le=1)]


class Ventilation(Model, table=True):
    __tablename__ = "ventilation"  # type: ignore
    TOPIC: ClassVar[str] = "domestic/ventilation"
    id: Annotated[str, Field(primary_key=True)]
    actual_co2: float | None
    co2_setpoint: float | None


class RoomTemperatureSetpoint(Message):
    TOPIC: ClassVar[str] = "domestic/control/room-temperature-setpoint/:id"
    temperature: float


class RoomHumiditySetpoint(Message):
    TOPIC: ClassVar[str] = "domestic/control/room-humidity-setpoint/:id"
    humidity: float


class RoomCo2Setpoint(Message):
    TOPIC: ClassVar[str] = "domestic/control/room-co2-setpoint/:id"
    co2: float
