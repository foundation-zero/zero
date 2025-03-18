# Per https://docs.google.com/document/d/11EGlLqZ21uHy4ICmhvPx9uKOwm0guKgWxY6-1zSQ2mQ/edit?tab=t.0#heading=h.l7ph84h61wda
from dataclasses import dataclass
from typing import Annotated, Any, get_args

from pydantic import AfterValidator, Field


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
    
def validate_ratio_within_precision(value: float) -> float:
    if value < 0 and value > -1e-10:
        return 0.0
    if value > 1 and value < 1 + 1e-10:
        return 1.0
    if 1 < value < 0:
        raise ValueError(f"Value {value} is outside bounds.")
    return value

type Celsius = Annotated[float, Field(ge=-273.15), UnitMeta(modelica_name="C")]
type LMin = Annotated[float, Field(ge=0), UnitMeta(modelica_name="l_min")]
type Hz = Annotated[float, Field(ge=0), UnitMeta(modelica_name="Hz")]
type Ratio = Annotated[
    float, AfterValidator(validate_ratio_within_precision), UnitMeta(modelica_name="ratio")
]
type Bar = Annotated[float, Field(ge=0), UnitMeta(modelica_name="Bar")]
type Watt = Annotated[float, UnitMeta(modelica_name="Watt")]
type seconds = Annotated[float, UnitMeta(modelica_name="s")]
type OnOff = Annotated[bool, UnitMeta(modelica_name="bool")]
