from dataclasses import dataclass
from enum import Enum

import strawberry
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext

from loads.api.db import SessionManager
from loads.api.messaging import Messaging


@dataclass
class LoadsContext(BaseContext):
    messaging: Messaging
    sessionmanager: SessionManager
    references_loader: (
        "DataLoader[tuple[strawberry.ID, CaseInput], ReferenceValue | None]"
    )
    variables_loader: "DataLoader[str, VariableType | None]"


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


@strawberry.enum
class WindDirection(Enum):
    port = "port"
    starboard = "starboard"


@strawberry.input
class CaseInput:
    awa_range: AwaRange
    aws_range: AwsRange
    wind_direction: WindDirection
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

    @strawberry.field
    def value(self, info: strawberry.Info[LoadsContext]) -> float | None:
        return info.context.messaging.get_variable_value(self.id)


@strawberry.type
class SailType:
    id: strawberry.ID
    abbreviation: str
    position_id: str
    name: str
    variant_name: str


@strawberry.type
class AlarmType:
    id: str
    name: str
    actual_variable_id: strawberry.Private[strawberry.ID]

    @strawberry.field
    def active(self, info: strawberry.Info[LoadsContext]) -> bool | None:
        return info.context.messaging.get_alarm_active_for(self.id)

    @strawberry.field
    def actual_value(self, info: strawberry.Info[LoadsContext]) -> float | None:
        return info.context.messaging.get_alarm_actual_for(self.id)

    @strawberry.field
    def threshold_value(self, info: strawberry.Info[LoadsContext]) -> float | None:
        return info.context.messaging.get_alarm_threshold_for(self.id)

    @strawberry.field
    def actual(self) -> "Variable":
        return Variable(id=self.actual_variable_id)


@strawberry.type
class Variable:
    id: strawberry.ID

    @strawberry.field
    async def actual(self) -> ActualType | None:
        return ActualType(id=str(self.id))

    @strawberry.field
    async def variable(
        self, info: strawberry.Info[LoadsContext]
    ) -> VariableType | None:
        return await info.context.variables_loader.load(self.id)

    @strawberry.field
    async def reference(
        self,
        info: strawberry.Info[LoadsContext],
        case: CaseInput,
    ) -> ReferenceValue | None:
        return await info.context.references_loader.load((self.id, case))
