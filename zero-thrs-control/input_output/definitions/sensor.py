from input_output.base import Stamped, ThrsModel
from input_output.definitions.units import Bar, Celsius, Hz, LMin, Ratio, seconds


class FlowSensor(ThrsModel):
    flow: Stamped[LMin]
    temperature: Stamped[Celsius]


class Pump(ThrsModel):
    speed: Stamped[Hz]
    op_time: Stamped[seconds]
    flow: Stamped[LMin]


class TemperatureSensor(ThrsModel):
    temperature: Stamped[Celsius]


class Valve(ThrsModel):
    position_rel: Stamped[Ratio]


class PressureSensor(ThrsModel):
    pressure: Stamped[Bar]
