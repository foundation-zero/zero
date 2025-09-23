import strawberry

from enum import Enum


@strawberry.enum
class Unit(Enum):
    TONNE = "tonne"
    PERCENTAGE = "percentage"
    METERS = "meters"
    KNOT = "knot"


@strawberry.enum
class SeaState(Enum):
    WET = "wet"
    DRY = "dry"


@strawberry.enum
class ThrusterMode(Enum):
    PROPULSION = "propulsion"
    REGENERATION = "regeneration"
    IDLE = "idle"


@strawberry.input
class PCSModeInput:
    fwd: ThrusterMode
    aft: ThrusterMode


@strawberry.input
class CaseInput:
    sails: list[str]
    sea_state: SeaState
    pcs_mode: PCSModeInput
    awa: float
    aws: float


@strawberry.type
class MastType:
    id: str
    name: str


@strawberry.type
class ValueType:
    id: strawberry.ID
    name: str


@strawberry.type
class TargetType:
    target: str
    unit: Unit


@strawberry.type
class AlertType:
    error_too_low: float | None
    warning_too_low: float | None
    warning_too_high: float | None
    error_too_high: float | None


@strawberry.type
class ReferenceValueType:
    value: ValueType
    masts: MastType | None
    target: TargetType
    ranges: AlertType
