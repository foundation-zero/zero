from input_output.base import Stamped, ThrsModel
from input_output.units import Bar, Celsius, Hz, LMin, Ratio


class FlowSensor(ThrsModel):
    flow: Stamped[LMin]
    temperature: Stamped[Celsius]


class Pump(ThrsModel):
    speed: Stamped[Hz]


class TemperatureSensor(ThrsModel):
    temperature: Stamped[Celsius]


class Valve(ThrsModel):
    relative_position: Stamped[Ratio]


class PressureSensor(ThrsModel):
    pressure: Stamped[Bar]
