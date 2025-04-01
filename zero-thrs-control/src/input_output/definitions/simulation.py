
from input_output.base import Stamped, StampedDf, ThrsModel
from input_output.definitions.units import Celsius, LMin, Ratio, Watt

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
