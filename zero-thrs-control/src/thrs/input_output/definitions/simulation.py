from typing import Annotated

from thrs.input_output.base import Stamped, ThrsValues, field_meta
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    LMin,
    OnOff,
    Overpressure,
    PcsMode,
    Watt,
)


class HeatSource(ThrsValues):
    heat_flow: Stamped[Watt]


class HvacExchanger(ThrsValues):
    heat_flow: Stamped[Watt]
    maximum_temperature: Stamped[Celsius]


class Boundary(ThrsValues):
    temperature: Stamped[Celsius]
    flow: Stamped[LMin]


class ExchangerBoundary(ThrsValues):
    flow: Stamped[LMin]
    temperature_supply: Stamped[Celsius]
    temperature_return: Stamped[Celsius]


class OverpressureTemperatureBoundary(ThrsValues):
    temperature: Stamped[Celsius]
    overpressure: Stamped[Overpressure]


class TemperatureBoundary(ThrsValues):
    temperature: Stamped[Celsius]


class PressureBoundary(ThrsValues):
    pressure: Stamped[Bar]


class FlowBoundary(ThrsValues):
    flow: Stamped[LMin]


class Thruster(HeatSource):
    active: Annotated[Stamped[bool], field_meta(included_in_fmu=False)]


class PropulsionDrive(HeatSource):
    active: Annotated[Stamped[bool], field_meta(included_in_fmu=False)]


class Converter(HeatSource):
    active: Annotated[Stamped[bool], field_meta(included_in_fmu=False)]


class Pcs(ThrsValues):
    mode: Annotated[
        Stamped[PcsMode],
        field_meta(included_in_fmu=False),
    ]


class AdsorptionChiller(ThrsValues):
    free_cooling: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]


__all__ = [
    "AdsorptionChiller",
    "Boundary",
    "ExchangerBoundary",
    "FlowBoundary",
    "HeatSource",
    "HvacExchanger",
    "OverpressureTemperatureBoundary",
    "Pcs",
    "TemperatureBoundary",
    "Thruster",
]
