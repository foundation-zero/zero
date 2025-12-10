from typing import Annotated
from thrs.input_output.base import Stamped, StampedDf, ThrsValues, field_meta
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    LMin,
    Overpressure,
    PcsMode,
    Ratio,
    Watt,
)
from pydantic.json_schema import SkipJsonSchema

type Stamp[T] = Stamped[T] | SkipJsonSchema[StampedDf[T]]


class HeatSource(ThrsValues):
    heat_flow: Stamp[Watt]


class Boundary(ThrsValues):
    temperature: Stamp[Celsius]
    flow: Stamp[LMin]


class FmuBoundary(ThrsValues):
    temperature: Stamp[Celsius]
    flow: Stamp[LMin]
    overpressure: Stamp[Overpressure]


class TemperatureBoundary(ThrsValues):
    temperature: Stamp[Celsius]


class PressureBoundary(ThrsValues):
    pressure: Stamp[Bar]


class FlowBoundary(ThrsValues):
    flow: Stamp[LMin]


class ValvePosition(ThrsValues):
    position_rel: Stamp[Ratio]


class Thruster(HeatSource):
    active: Annotated[Stamp[bool], field_meta(included_in_fmu=False)]


class Pcs(ThrsValues):
    mode: Annotated[
        Stamp[PcsMode],
        field_meta(included_in_fmu=False),
    ]


__all__ = [
    "HeatSource",
    "Boundary",
    "TemperatureBoundary",
    "FlowBoundary",
    "ValvePosition",
    "Thruster",
    "Pcs",
]
