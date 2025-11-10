from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    Charged,
    Hz,
    Kelvin,
    LMin,
    OnOff,
    OptionalCelsius,
    PcsMode,
    Ratio,
    seconds,
    Watt,
)


class FlowSensor(ThrsModel):
    flow: Stamped[LMin]
    temperature: Stamped[Celsius]


class Pump(ThrsModel):
    speed: Stamped[Hz]
    op_time: Stamped[seconds]
    flow: Stamped[LMin]


class TemperatureSensor(ThrsModel):
    temperature: Stamped[Celsius]


class CalculatedTemperature(ThrsModel):
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


class Valve(ThrsModel):
    position_rel: Stamped[Ratio]


class PressureSensor(ThrsModel):
    pressure: Stamped[Bar]


class Thruster(ThrsModel):
    active: Stamped[bool]


class Pcs(ThrsModel):
    mode: Stamped[PcsMode]


class Pcm(ThrsModel):
    charged: Stamped[Charged]


class Fahrenheit(ThrsModel):
    operating: Stamped[OnOff]


class PowerSensor(ThrsModel):
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
]
