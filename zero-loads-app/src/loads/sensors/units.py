from dataclasses import dataclass
from typing import Annotated, Callable, TypeAlias

from pydantic import BeforeValidator, Field


@dataclass
class VariableMeta:
    unit: str | None = None
    name: str | None = None
    ignore: bool = False


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
    VariableMeta(unit="ratio", name="relative-position"),
    BeforeValidator(per_mille_to_ratio),
    ScalingMeta(
        conversion=per_mille_to_ratio,
        inverse_conversion=ratio_to_per_mille,
    ),
]
Position: TypeAlias = Annotated[
    int, Field(ge=0), VariableMeta(unit="mm", name="position")
]
Load: TypeAlias = Annotated[
    float,
    Field(ge=0, le=20),  # this should go on the model field
    VariableMeta(unit="tonne", name="load"),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
]
Alarm: TypeAlias = bool
Lock: TypeAlias = bool
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
