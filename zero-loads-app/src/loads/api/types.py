from enum import Enum

import strawberry


@strawberry.enum
class Unit(Enum):
    tonne = "tonne"
    percentage = "percentage"
    meters = "meters"
    knot = "knot"


@strawberry.enum
class SeaState(Enum):
    wet = "wet"
    dry = "dry"


@strawberry.enum
class ThrusterMode(Enum):
    propulsion = "propulsion"
    regeneration = "regeneration"
    idle = "idle"


@strawberry.enum
class Sails(Enum):
    full_main_sail = "full-main-sail"
    main_sail_reef1 = "main-sail-reef1"
    main_sail_reef2 = "main-sail-reef2"
    main_blade = "main-blade"
    main_staysail = "main-staysail"
    full_mizzen_sail = "full-mizzen-sail"
    mizzen_sail_reef1 = "mizzen-sail-reef1"
    mizzen_sail_reef2 = "mizzen-sail-reef2"
    mizzen_jib = "mizzen-jib"
    mizzen_staysail = "mizzen-staysail"


@strawberry.type
class MastType:
    id: str
    name: str


@strawberry.type
class ValueType:
    id: strawberry.ID
    name: str


@strawberry.type
class ActualType:
    id: str
    value: float | None


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


@strawberry.input
class PCSModeInput:
    fwd: ThrusterMode
    aft: ThrusterMode


@strawberry.input
class CaseInput:
    sea_state: SeaState
    pcs_mode: PCSModeInput
    awa: float
    aws: float
