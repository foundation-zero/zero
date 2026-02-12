from enum import Enum

import strawberry


@strawberry.enum
class Unit(Enum):
    tonne = "tonne"
    ratio = "ratio"
    bool = "bool"
    mm = "mm"
    knots = "knots"
    degrees = "degrees"


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


@strawberry.input
class CaseInput:
    awa_range: AwaRange
    aws_range: AwsRange
    sailset: list[strawberry.ID]

    def __hash__(self) -> int:
        return hash((self.awa_range, self.aws_range, tuple(self.sailset)))


@strawberry.type
class VariableType:
    id: strawberry.ID
    name: str
    unit: Unit | None
    scale_min: float | None
    scale_max: float | None
    scale_min_label: str | None
    scale_max_label: str | None


@strawberry.input
class ReferenceValueInput:
    id: strawberry.ID
    alarm_low: float | None = None
    warning_low: float | None = None
    target: float | None = None
    warning_high: float | None = None
    alarm_high: float | None = None


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


@strawberry.type
class SailType:
    id: strawberry.ID
    abbreviation: str
    position_id: str
    name: str
    variant_name: str
