from typing import Annotated
from input_output.base import FieldMeta, Stamped, StampedDf, ThrsModel
from input_output.definitions.units import Celsius, LMin, PcsMode, Ratio, Watt

type Stamp[T] = Stamped[T] | StampedDf[T]


class HeatSource(ThrsModel):
    heat_flow: Stamp[Watt]


class Boundary(ThrsModel):
    temperature: Stamp[Celsius]
    flow: Stamp[LMin]


class TemperatureBoundary(ThrsModel):
    temperature: Stamp[Celsius]


class FlowBoundary(ThrsModel):
    flow: Stamp[LMin]


class ValvePosition(ThrsModel):
    position_rel: Stamp[Ratio]


class Thruster(HeatSource):
    active: Annotated[Stamp[bool], FieldMeta(included_in_fmu=False)]


class Pcs(ThrsModel):
    mode: Annotated[
        Stamped[PcsMode],
        FieldMeta(included_in_fmu=False),
    ]
