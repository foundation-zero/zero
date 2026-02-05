from enum import Enum

import strawberry


@strawberry.enum
class Unit(Enum):
    tonne = "tonne"
    ratio = "ratio"
    bool = "bool"


@strawberry.enum
class AwaRange(Enum):
    upwind = "upwind"
    reaching = "reaching"
    downwind = "downwind"


@strawberry.enum
class AwsRange(Enum):
    aws_0_10 = "[0,10)"
    aws_10_15 = "[10,15)"
    aws_15_20 = "[15,20)"
    aws_20_25 = "[20,25)"
    aws_25_30 = "[25,30)"
    aws_30_40 = "[30,40)"
    aws_40_plus = "[40,)"


@strawberry.enum
class Sails(Enum):
    full_main = "full-main"
    main_reef1 = "main-reef1"
    main_reef2 = "main-reef2"
    main_reef3 = "main-reef3"
    trisail = "trisail"
    utility = "utility"
    full_mizzen = "full-mizzen"
    mizzen_reef1 = "mizzen-reef1"
    mizzen_reef2 = "mizzen-reef2"
    blade = "blade"
    code_zero = "code-zero"
    A3 = "A3"
    A2 = "A2"
    storm_jib = "storm-jib"
    staysail = "staysail"
    mizzen_jib = "mizzen-jib"
    mizzen_staysail = "mizzen-staysail"


@strawberry.input
class CaseInput:
    awa_range: AwaRange
    aws_range: AwsRange
    sailset: list[Sails]


@strawberry.type
class VariableType:
    id: strawberry.ID
    name: str
    unit: Unit
    minimum: float | None
    maximum: float | None


@strawberry.type
class ReferenceValue:
    id: strawberry.ID
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
