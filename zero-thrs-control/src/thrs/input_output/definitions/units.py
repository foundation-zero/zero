# Per https://docs.google.com/document/d/11EGlLqZ21uHy4ICmhvPx9uKOwm0guKgWxY6-1zSQ2mQ/edit?tab=t.0#heading=h.l7ph84h61wda
from dataclasses import dataclass
from enum import Enum
from types import GenericAlias, UnionType
from typing import (
    Annotated,
    Any,
    Literal,
    TypeAlias,
    TypeAliasType,
    get_args,
    get_origin,
)
from typing_extensions import _AnnotatedAlias

from pydantic import AfterValidator, Field


@dataclass(eq=True, frozen=True)
class UnitMeta:
    modelica_name: str


def _unit_for_single_annotation(annotation: Any) -> Any | None:
    if hasattr(annotation, "__pydantic_generic_metadata__"):
        return next(iter(annotation.__pydantic_generic_metadata__["args"]), None)
    else:
        return annotation


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
            (meta for meta in get_args(unit) if isinstance(meta, UnitMeta)),
            None,
        )
        if unit
        else None
    )


def zero_for_unit(unit: Any) -> Any:
    if isinstance(unit, TypeAliasType):
        unit = unit.__value__
        if isinstance(unit, _AnnotatedAlias):
            unit = get_args(unit)[0]

    elif get_origin(unit) is Annotated:
        unit = get_args(unit)[0]
    if unit is float:
        return 0.0
    elif unit == float | None:
        return None
    elif get_origin(unit) is Literal:
        return get_args(unit)[0]
    elif issubclass(unit, Enum):
        return next(e for e in unit)
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


def validate_nonzero_float_within_precision(
    value: float, tolerance: float = 1e-7
) -> float:
    if value < 0 and value > -tolerance:
        return 0.0
    if value < -tolerance:
        raise ValueError(f"Value {value} is outside bounds.")
    return value


OptionalCelsius: TypeAlias = Annotated[
    float | None, Field(ge=-273.15), UnitMeta(modelica_name="C")
]
Celsius: TypeAlias = Annotated[float, Field(ge=-273.15), UnitMeta(modelica_name="C")]
Kelvin: TypeAlias = Annotated[float, Field(ge=0), UnitMeta(modelica_name="K")]
LMin: TypeAlias = Annotated[
    float,
    Field(ge=-0.1),
    UnitMeta(modelica_name="l_min"),
]
Hz: TypeAlias = Annotated[float, Field(ge=-0.1), UnitMeta(modelica_name="Hz")]
Ratio: TypeAlias = Annotated[
    float,
    AfterValidator(validate_ratio_within_precision),
    UnitMeta(modelica_name="ratio"),
]
Bar: TypeAlias = Annotated[float, Field(ge=-1e-2), UnitMeta(modelica_name="Bar")]
Watt: TypeAlias = Annotated[float, UnitMeta(modelica_name="Watt")]
seconds: TypeAlias = Annotated[float, UnitMeta(modelica_name="s")]
Joule: TypeAlias = Annotated[float, UnitMeta(modelica_name="Joule")]
OnOff: TypeAlias = Annotated[bool, UnitMeta(modelica_name="bool")]
NoError: TypeAlias = Annotated[bool, UnitMeta(modelica_name="bool")]
Error: TypeAlias = Annotated[bool, UnitMeta(modelica_name="bool")]
Operating: TypeAlias = Annotated[bool, UnitMeta(modelica_name="bool")]
Charged: TypeAlias = Annotated[bool, UnitMeta(modelica_name="bool")]
Tuning: TypeAlias = tuple[float, float, float]
Overpressure: TypeAlias = Annotated[float, UnitMeta(modelica_name="Bar")]
Liter: TypeAlias = Annotated[float, Field(ge=0), UnitMeta(modelica_name="Liter")]


class PcsMode(Enum):
    OFF = "off"
    MANEUVERING = "maneuvering"
    PROPULSION = "propulsion"
    REGENERATION = "regeneration"


# FahrenheitMode: OFF=0, ON=1, VALVE_RUN=2, ACTIVATION=3
FahrenheitMode: TypeAlias = Literal[0, 1, 2, 3]

# FreeCoolingMode: OFF=0, ON=1, AUTO=2
FreeCoolingMode: TypeAlias = Literal[0, 1, 2]

# TankControlMode: NONE=0, BOTH=1, COLD=2, HOT=3
TankControlMode: TypeAlias = Literal[0, 1, 2, 3]


class TankControlModeEnum(Enum):
    NONE = 0
    BOTH = 1
    COLD = 2
    HOT = 3


class FahrenheitModeEnum(Enum):
    OFF = 0
    ON = 1
    VALVE_RUN = 2
    ACTIVATION = 3


class FreeCoolingModeEnum(Enum):
    OFF = 0
    ON = 1
    AUTO = 2
