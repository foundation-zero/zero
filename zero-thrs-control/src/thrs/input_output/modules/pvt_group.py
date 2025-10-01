from thrs.input_output.base import ThrsModel
from thrs.input_output.definitions import control, sensor


class PvtGroupSensorValues(ThrsModel):
    pump: sensor.Pump
    temperature_supply: sensor.TemperatureSensor
    temperature_return: sensor.TemperatureSensor
    pressure: sensor.PressureSensor
    mix: sensor.Valve
    max_temperature_strings: sensor.CalculatedTemperature


class PvtGroupControlValues(ThrsModel):
    pump: control.Pump
    mix: control.Valve
