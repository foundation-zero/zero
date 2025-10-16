from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    Charged,
    Hz,
    LMin,
    OptionalCelsius,
    PcsMode,
    Ratio,
    seconds,
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
]
