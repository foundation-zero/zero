from enum import Enum

import strawberry


@strawberry.enum
class Unit(Enum):
    tonne = "tonne"
    promille = "promille"
    on_off = "on-off"


@strawberry.enum
class Sails(Enum):
    full_main = "full-main"
    main_reef1 = "main-reef1"
    main_reef2 = "main-reef2"
    main_reef3 = "main-reef3"
    trisail = "trisail"
    full_mizzen = "full-mizzen"
    mizzen_reef1 = "mizzen-reef1"
    mizzen_reef2 = "mizzen-reef2"
    blade = "blade"
    code_zero = "code-zero"
    genoa = "genoa"
    gennaker = "gennaker"
    storm_jib = "storm-jib"
    staysail = "staysail"
    mizzen_jib = "mizzen-jib"
    mizzen_genoa = "mizzen-genoa"


@strawberry.input
class CaseInput:
    awa: float
    aws: float
    sailset: list[Sails]


@strawberry.type
class VariableType:
    id: strawberry.ID
    name: str
    unit: Unit


@strawberry.type
class ReferenceValue:
    alarm_low: float | None
    warning_low: float | None
    target: float | None
    warning_high: float | None
    alarm_high: float | None


@strawberry.type
class ReferenceValueType:
    variable: VariableType
    reference: ReferenceValue


@strawberry.type
class ActualType:
    id: str
    value: float | None
