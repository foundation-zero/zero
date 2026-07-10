from dataclasses import dataclass
from typing import Annotated, Callable, Literal, TypeAlias

from pydantic import Field

from loads.util import hyphenize


@dataclass
class VariableMeta:
    unit: str | None = None
    name: str | None = None
    key: str | None = None
    display_name: str | None = None
    scale_min: float | None = None
    scale_max: float | None = None
    scale_min_label: str | None = None
    scale_max_label: str | None = None
    type: Literal["actual", "alarm", "alarm_threshold"] | None = None
    alarm_for: str | None = None
    threshold_for: str | None = None
    variable_key: str | None = None
    applies_to_tack: Literal["port", "starboard"] | None = None

    @property
    def is_actual(self) -> bool:
        return self.type == "actual"

    @property
    def is_alarm(self) -> bool:
        return self.type == "alarm"

    def override(self, other: "VariableMeta") -> "VariableMeta":
        return VariableMeta(
            unit=other.unit or self.unit,
            name=other.name or self.name,
            display_name=other.display_name or self.display_name,
            type=other.type or self.type,
            alarm_for=other.alarm_for or self.alarm_for,
            threshold_for=other.threshold_for or self.threshold_for,
            scale_min=other.scale_min
            if other.scale_min is not None
            else self.scale_min,
            scale_max=other.scale_max
            if other.scale_max is not None
            else self.scale_max,
            scale_min_label=other.scale_min_label or self.scale_min_label,
            scale_max_label=other.scale_max_label or self.scale_max_label,
            variable_key=other.variable_key or self.variable_key,
            applies_to_tack=other.applies_to_tack or self.applies_to_tack,
        )

    @property
    def alarm_for_field(self) -> str | None:
        return (
            hyphenize(self.alarm_for)
            if self.type == "alarm" and self.alarm_for
            else None
        )


@dataclass
class ScalingMeta:
    conversion: Callable
    inverse_conversion: Callable


def per_mille_to_ratio(value: int) -> float:
    return value / 1000.0


def ratio_to_per_mille(value: float) -> int:
    return int(value * 1000.0)


def tonne_to_decakilogram(value: float) -> int:
    return int(value * 100.0)


def decakilogram_to_tonne(value: int) -> float:
    return value / 100.0


RelativePosition: TypeAlias = Annotated[
    float,
    Field(ge=0, le=1),
    VariableMeta(unit="ratio", scale_min=0, scale_max=1, type="actual"),
]
Position: TypeAlias = Annotated[
    int,
    Field(ge=0),
    VariableMeta(unit="mm", scale_min=0, type="actual"),
]

Load: TypeAlias = Annotated[
    float,
    VariableMeta(unit="tonne", type="actual"),
]
MaxLoad: TypeAlias = Annotated[
    float,
    VariableMeta(unit="tonne", type="alarm_threshold"),
]
Alarm: TypeAlias = Annotated[bool, VariableMeta(type="alarm")]
Lock: TypeAlias = Annotated[bool, VariableMeta(unit="bool", type="actual")]
Speed: TypeAlias = Annotated[
    float,
    Field(ge=0),
    VariableMeta(unit="knots"),
]
Angle: TypeAlias = Annotated[
    float,
    Field(ge=-180, le=180),
    VariableMeta(unit="degrees"),
]
