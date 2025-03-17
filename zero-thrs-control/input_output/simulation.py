from input_output.base import Stamped, ThrsModel
from input_output.units import Celsius, LMin, Watt


class HeatSource(ThrsModel):
    heat_flow: Stamped[Watt]


class Boundary(ThrsModel):
    temperature: Stamped[Celsius]
    flow: Stamped[LMin]
