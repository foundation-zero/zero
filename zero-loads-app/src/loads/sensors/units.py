from dataclasses import dataclass
from typing import Annotated, TypeAlias

from pydantic import (
    Field,
)


@dataclass(frozen=True)
class Unit:
    unit: str


Position: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="mm")]
RelativePosition: TypeAlias = Annotated[float, Field(ge=0, lt=1000), Unit(unit="‰")]
Load: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="tonne")]
Torque: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="Nm")]
RotationalSpeed: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="rpm")]
Temperature: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="°C")]
