from dataclasses import dataclass
from typing import Annotated, Callable, Literal, TypeAlias

from pydantic import BeforeValidator, Field

from loads.util import hyphenize


@dataclass
class VariableMeta:
    unit: str | None = None
    name: str | None = None
    display_name: str | None = None
    scale_min: float | None = None
    scale_max: float | None = None
    scale_min_label: str | None = None
    scale_max_label: str | None = None
    type: Literal["actual", "alarm", "alarm_threshold"] | None = None
    alarm_for: str | None = None

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
            scale_min=other.scale_min or self.scale_min,
            scale_max=other.scale_max or self.scale_max,
            scale_min_label=other.scale_min_label or self.scale_min_label,
            scale_max_label=other.scale_max_label or self.scale_max_label,
        )

    @property
    def alarm_for_field(self) -> str | None:
        return hyphenize(self.alarm_for or "load") if self.type == "alarm" else None


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
    Field(ge=0, le=1, validation_alias="relative_position_dummy"),
    VariableMeta(unit="ratio", name="relative-position", scale_min=0, scale_max=1),
    BeforeValidator(per_mille_to_ratio),
    ScalingMeta(
        conversion=per_mille_to_ratio,
        inverse_conversion=ratio_to_per_mille,
    ),
]
Position: TypeAlias = Annotated[
    int,
    Field(ge=0, validation_alias="ow_ActPos_mm"),
    VariableMeta(unit="mm", name="position", scale_min=0, scale_max=100),
]

LoadBase: TypeAlias = Annotated[  # Needed to be able to override Field constraints where needed (e.g. in Vang). Pydantic has no fixed order to resolve nested `Field`s in inside of `Annotated`s
    float,
    Field(validation_alias="ow_ActLoad_10kg"),
    VariableMeta(unit="tonne", name="load", scale_min=0, scale_max=20),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
]

Load: TypeAlias = Annotated[LoadBase, Field(ge=0, le=20)]

ReliefLoad: TypeAlias = Annotated[
    float,
    Field(ge=0, le=20, validation_alias="ow_RelfLoad_10kg"),
    VariableMeta(unit="tonne", name="relief_load", type="alarm_threshold"),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
]
Alarm: TypeAlias = Annotated[
    bool,
    Field(validation_alias="ox_LoadAlarm"),
    VariableMeta(unit="bool", name="alarm", type="alarm"),
]
Lock: TypeAlias = Annotated[bool, VariableMeta(unit="bool")]
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
