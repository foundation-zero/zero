from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    Charged,
    Hz,
    Kelvin,
    LMin,
    Liter,
    OnOff,
    OptionalCelsius,
    PcsMode,
    Ratio,
    seconds,
    Watt,
)


class FlowSensor(ThrsValues):
    flow: Stamped[LMin]
    temperature: Stamped[Celsius]


class Pump(ThrsValues):
    speed: Stamped[Hz]
    op_time: Stamped[seconds]
    flow: Stamped[LMin]


class TemperatureSensor(ThrsValues):
    temperature: Stamped[Celsius]


class LevelSensor(ThrsValues):
    level: Stamped[Liter]


class CalculatedTemperature(ThrsValues):
    temperature: Stamped[OptionalCelsius]

    @classmethod
    def from_max_temperature(cls, sensors: list[TemperatureSensor]):
        max_sensor = max(sensors, key=lambda sensor: sensor.temperature.value)

        return CalculatedTemperature(
            temperature=Stamped(
                value=max_sensor.temperature.value,
                timestamp=max_sensor.temperature.timestamp,
            )
        )


class Valve(ThrsValues):
    position_rel: Stamped[Ratio]


class PressureSensor(ThrsValues):
    pressure: Stamped[Bar]


class Thruster(ThrsValues):
    active: Stamped[bool]


class Pcs(ThrsValues):
    mode: Stamped[PcsMode]


class Pcm(ThrsValues):
    charged: Stamped[Charged]


class Fahrenheit(ThrsValues):
    operating: Stamped[OnOff]


class PowerSensor(ThrsValues):
    flow: Stamped[LMin]
    power: Stamped[Watt]
    delta_t: Stamped[Kelvin]
    temperature_warm: Stamped[Celsius]
    temperature_cold: Stamped[Celsius]


__all__ = [
    "FlowSensor",
    "Pump",
    "TemperatureSensor",
    "CalculatedTemperature",
    "Valve",
    "PressureSensor",
    "Thruster",
    "Pcs",
    "Pcm",
    "Fahrenheit",
    "PowerSensor",
    "LevelSensor",
]
