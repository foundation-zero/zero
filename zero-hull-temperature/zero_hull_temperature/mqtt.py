from typing import Annotated

from pydantic import BaseModel, Field


class MqttValue(BaseModel):
    value: Annotated[bool, Field(serialization_alias="Value")]


class TemperatureReading(BaseModel):
    sensor: str
    temperature: float


class Temperatures(BaseModel):
    temperatures: dict[str, float]
