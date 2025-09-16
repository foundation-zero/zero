import strawberry
from enum import Enum


@strawberry.enum
class Unit(Enum):
    tonne = "tonne"
    percentage = "percentage"
    meters = "meters"
    knots = "knots"


@strawberry.enum
class SeaState(Enum):
    wet = "wet"
    dry = "dry"


@strawberry.enum
class ThrusterMode(Enum):
    propulsion = "propulsion"
    regeneration = "regeneration"
    idle = "idle"


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
class ValueType:
    id: strawberry.ID
    name: str


@strawberry.type
class RangesType:
    error_too_low: float | None
    warning_too_low: float | None
    warning_too_high: float | None
    error_too_high: float | None


@strawberry.type
class ReferenceValueType:
    value: ValueType
    target: float
    ranges: RangesType
    unit: Unit


# @strawberry.type
# class ReferenceValueType:
#     id: strawberry.ID
#     sail_set_id: str
#     condition_id: str
#     mast_id: str
#     value_definition_id: str
#     value: float
#     error_too_low: float | None
#     error_too_high: float | None
#     warning_too_low: float | None
#     warning_too_high: float | None
