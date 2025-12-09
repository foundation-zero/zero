from typing import Annotated
from thrs.input_output.base import Stamped, StampedDf, ThrsModel, field_meta
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


class HeatSource(ThrsModel):
    heat_flow: Stamp[Watt]


class Boundary(ThrsModel):
    temperature: Stamp[Celsius]
    flow: Stamp[LMin]


class FmuBoundary(ThrsModel):
    temperature: Stamp[Celsius]
    flow: Stamp[LMin]
    overpressure: Stamp[Overpressure]


class TemperatureBoundary(ThrsModel):
    temperature: Stamp[Celsius]


class PressureBoundary(ThrsModel):
    pressure: Stamp[Bar]


class FlowBoundary(ThrsModel):
    flow: Stamp[LMin]


class ValvePosition(ThrsModel):
    position_rel: Stamp[Ratio]


class Thruster(HeatSource):
    active: Annotated[Stamp[bool], field_meta(included_in_fmu=False)]


class Pcs(ThrsModel):
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
