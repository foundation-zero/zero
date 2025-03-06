from input_output.base import Stamped, ThrsModel
from input_output.units import Ratio


class Pump(ThrsModel):
    dutypoint: Stamped[Ratio]
    on: Stamped[bool]


class Valve(ThrsModel):
    setpoint: Stamped[Ratio]
