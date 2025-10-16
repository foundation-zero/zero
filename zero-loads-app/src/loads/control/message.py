from enum import Enum
from typing import ClassVar

from pydantic import BaseModel


class Message(BaseModel):
    TOPIC: ClassVar[str]


class ThrusterMode(Enum):
    propulsion = "propulsion"
    regeneration = "regeneration"
    idle = "idle"


class PCSModeInput(BaseModel):
    fwd: ThrusterMode
    aft: ThrusterMode


class SensorInput(Message):
    TOPIC: ClassVar[str] = "loads/sensor_input"
    awa: float
    aws: float
    pcs_mode: PCSModeInput
    sails: list[str]


class Conditions(Message):
    TOPIC: ClassVar[str] = "loads/conditions"
    sea_state: str
    awa: float
    aws: float
    pcs_mode: PCSModeInput
    sails: list[str]
