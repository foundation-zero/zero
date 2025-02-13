from simulation.io.base import Stamped, ThrsModel
from simulation.io.units import Ratio


class Pump(ThrsModel):
    dutypoint: Stamped[Ratio]
    on: Stamped[bool]


class Valve(ThrsModel):
    setpoint: Stamped[Ratio]
