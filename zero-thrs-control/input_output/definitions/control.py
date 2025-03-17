from input_output.base import Stamped, ThrsModel
from input_output.definitions.units import OnOff, Ratio


class Pump(ThrsModel):
    dutypoint: Stamped[Ratio]
    on: Stamped[OnOff]


class Valve(ThrsModel):
    setpoint: Stamped[Ratio]
