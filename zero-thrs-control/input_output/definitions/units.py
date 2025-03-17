# Per https://docs.google.com/document/d/11EGlLqZ21uHy4ICmhvPx9uKOwm0guKgWxY6-1zSQ2mQ/edit?tab=t.0#heading=h.l7ph84h61wda
from dataclasses import dataclass
from typing import Annotated, Any, get_args

from pydantic import Field


@dataclass(eq=True, frozen=True)
class UnitMeta:
    modelica_name: str


def unit_meta(unit: Any) -> UnitMeta | None:
    return (
        next(
            (meta for meta in get_args(unit.__value__) if isinstance(meta, UnitMeta)),
            None,
        )
        if unit and hasattr(unit, "__value__")
        else None
    )


type Celsius = Annotated[float, Field(ge=-273.15), UnitMeta(modelica_name="C")]
type LMin = Annotated[float, Field(ge=0), UnitMeta(modelica_name="l_min")]
type Hz = Annotated[float, Field(ge=0), UnitMeta(modelica_name="Hz")]
type Ratio = Annotated[
    float, UnitMeta(modelica_name="ratio")
]  # TODO: bound between 0 and 1 in fmu
type Bar = Annotated[float, Field(ge=0), UnitMeta(modelica_name="Bar")]
type Watt = Annotated[float, UnitMeta(modelica_name="Watt")]
type seconds = Annotated[float, UnitMeta(modelica_name="s")]
type OnOff = Annotated[bool, UnitMeta(modelica_name="bool")]
