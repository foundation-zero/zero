from dataclasses import dataclass
from typing import Annotated, Callable, TypeAlias

from pydantic import (
    BeforeValidator,
    Field,
)


@dataclass
class InverseConversion:
    conversion: Callable


def per_mille_to_ratio(value: int) -> float:
    return value / 1000.0


def ratio_to_per_mille(value: float) -> int:
    return int(value * 1000.0)


def tonne_to_decakilogram(value: float) -> int:
    return int(value * 100.0)


def decakilogram_to_tonne(value: int) -> float:
    return value / 100.0


RatioFromPerMille: TypeAlias = Annotated[
    float,
    Field(ge=0, le=1),
    BeforeValidator(per_mille_to_ratio),
    InverseConversion(ratio_to_per_mille),
]
Millimeter: TypeAlias = Annotated[int, Field(ge=0)]
TonneFromDecaKilogram: TypeAlias = Annotated[
    float,
    Field(ge=0),
    BeforeValidator(decakilogram_to_tonne),
    InverseConversion(tonne_to_decakilogram),
]
Alarm: TypeAlias = bool
