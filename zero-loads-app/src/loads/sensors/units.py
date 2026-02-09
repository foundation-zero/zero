from dataclasses import dataclass
from typing import Annotated, Callable, TypeAlias

from pydantic import BeforeValidator, Field


@dataclass
class VariableMeta:
    unit: str | None = None
    name: str | None = None
    display_name: str | None = None
    ignore: bool = False
    scale_min: float | None = None
    scale_max: float | None = None
    scale_min_label: str | None = None
    scale_max_label: str | None = None


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
    VariableMeta(unit="ratio", name="relative-position"),
    BeforeValidator(per_mille_to_ratio),
    ScalingMeta(
        conversion=per_mille_to_ratio,
        inverse_conversion=ratio_to_per_mille,
    ),
]
Position: TypeAlias = Annotated[
    int,
    Field(ge=0, validation_alias="ow_ActPos_mm"),
    VariableMeta(unit="mm", name="position"),
]
Load: TypeAlias = Annotated[
    float,
    Field(ge=0, le=20, validation_alias="ow_ActLoad_10kg"),
    VariableMeta(unit="tonne", name="load"),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
]
ReliefLoad: TypeAlias = Annotated[
    float,
    Field(ge=0, le=20, validation_alias="ow_RelfLoad_10kg"),
    VariableMeta(unit="tonne", name="relief_load", ignore=True),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
]
Alarm: TypeAlias = Annotated[
    bool,
    Field(validation_alias="ox_LoadAlarm"),
    VariableMeta(unit="bool", name="alarm", ignore=True),
]
Lock: TypeAlias = Annotated[bool, VariableMeta(unit="bool")]
Speed: TypeAlias = Annotated[
    float,
    Field(ge=0),
    VariableMeta(unit="knots", name="speed"),
]
Angle: TypeAlias = Annotated[
    float,
    Field(ge=-180, le=180),
    VariableMeta(unit="degrees", name="angle"),
]
