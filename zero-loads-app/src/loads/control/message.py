from enum import Enum

from typing import ClassVar
from pydantic import BaseModel


class Message(BaseModel):
    TOPIC: ClassVar[str]


class ThrusterMode(Enum):
    PROPULSION = "propulsion"
    REGENERATION = "regeneration"
    IDLE = "idle"


class PCSModeInput(BaseModel):
    fwd: ThrusterMode
    aft: ThrusterMode


class Conditions(Message):
    TOPIC: ClassVar[str] = "loads/risingwave/conditions"
    awa: float
    aws: float
    pcs_mode: PCSModeInput
    sails: list[str]


class Case(Message):
    TOPIC: ClassVar[str] = "loads/control/case"
    sea_state: str
    awa: float
    aws: float
    pcs_mode: PCSModeInput
    sails: list[str]
