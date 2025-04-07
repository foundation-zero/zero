# Per https://docs.google.com/document/d/11EGlLqZ21uHy4ICmhvPx9uKOwm0guKgWxY6-1zSQ2mQ/edit?tab=t.0#heading=h.l7ph84h61wda
from dataclasses import dataclass
from types import GenericAlias, UnionType
from typing import Annotated, Any, Literal, TypeAliasType, get_args, get_origin
from typing_extensions import _AnnotatedAlias

from pydantic import AfterValidator, Field


@dataclass(eq=True, frozen=True)
class UnitMeta:
    modelica_name: str


def _unit_for_single_annotation(annotation: Any) -> Any | None:
    return next(iter(annotation.__pydantic_generic_metadata__["args"]), None)  # type: ignore


def unit_for_annotation(annotation: Any) -> Any | None:
    if isinstance(annotation, GenericAlias):
        units = set(annotation.__args__)
        if len(units) > 1:
            raise ValueError("Generic alias of annotations with different units.")
        return next(iter(units))
    if isinstance(annotation, UnionType):
        units = set(
            _unit_for_single_annotation(annotation)
            for annotation in get_args(annotation)
        )
        if len(units) > 1:
            raise ValueError("Union of annotations with different units.")
        return next(iter(units))

    return _unit_for_single_annotation(annotation)


def unit_meta(unit: Any) -> UnitMeta | None:
    return (
        next(
            (meta for meta in get_args(unit.__value__) if isinstance(meta, UnitMeta)),
            None,
        )
        if unit and hasattr(unit, "__value__")
        else None
    )


def zero_for_unit(unit: Any) -> Any:
    if isinstance(unit, TypeAliasType):
        unit = unit.__value__
        if isinstance(unit, _AnnotatedAlias):
            unit = get_args(unit)[0]
    if unit is float:
        return 0.0
    elif get_origin(unit) is Literal:
        return get_args(unit)[0]
    elif unit is bool:
        return False
    else:
        raise ValueError(f"Unsupported unit type: {unit}")


def validate_ratio_within_precision(value: float, tolerance: float = 1e-4) -> float:
    if value < 0 and value > -tolerance:
        return 0.0
    if value > 1 and value < 1 + tolerance:
        return 1.0
    if value < 0 or value > 1:
        raise ValueError(f"Value {value} is outside bounds.")
    return value


def validate_flow_within_precision(value: float, tolerance: float = 2e-2) -> float:
    if value < 0 and value > -tolerance:
        return 0.0
    if value < -tolerance:
        raise ValueError(f"Value {value} is outside bounds.")
    return value


type Celsius = Annotated[float, Field(ge=-273.15), UnitMeta(modelica_name="C")]
type LMin = Annotated[
    float,
    AfterValidator(validate_flow_within_precision),
    UnitMeta(modelica_name="l_min"),
]
type Hz = Annotated[float, Field(ge=-1e-17), UnitMeta(modelica_name="Hz")]
type Ratio = Annotated[
    float,
    AfterValidator(validate_ratio_within_precision),
    UnitMeta(modelica_name="ratio"),
]
type Bar = Annotated[float, Field(ge=-0.2), UnitMeta(modelica_name="Bar")] #TODO: this becomes negative, need to figure out if that's OK
type Watt = Annotated[float, UnitMeta(modelica_name="Watt")]
type seconds = Annotated[float, UnitMeta(modelica_name="s")]
type OnOff = Annotated[bool, UnitMeta(modelica_name="bool")]
type PcsMode = Literal["off", "maneuvering", "propulsion", "regeneration"]
