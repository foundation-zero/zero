from typing import Optional
from pydantic import BaseModel


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
