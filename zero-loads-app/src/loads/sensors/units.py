from dataclasses import dataclass
from typing import Annotated, TypeAlias

from pydantic import (
    Field,
)


@dataclass(frozen=True)
class Unit:
    unit: str


Millimeter: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="mm")]
DeciKilogram: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="10Kg")]
Promille: TypeAlias = Annotated[float, Field(ge=0, lt=1000), Unit(unit="‰")]
