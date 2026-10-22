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
    active: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]


class PropulsionDrive(HeatSource):
    active: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]
    temp_power_stage: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    power: Annotated[Stamped[Watt], field_meta(included_in_fmu=False)]


class BrightloopConverter(ThrsValues):
    active: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]
    cell01_temperature1: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    cell01_temperature2: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    cell02_temperature1: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    cell02_temperature2: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    power: Annotated[Stamped[Watt], field_meta(included_in_fmu=False)]


class Ugrid(HeatSource):
    active: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]
    temp_power_stage: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    power: Annotated[Stamped[Watt], field_meta(included_in_fmu=False)]


class ShorePowerConverter(ThrsValues):
    active: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]
    esi_transformer_temperature: Annotated[
        Stamped[Celsius], field_meta(included_in_fmu=False)
    ]
    esi_igbt_min_temperature: Annotated[
        Stamped[Celsius], field_meta(included_in_fmu=False)
    ]
    esi_igbt_max_temperature: Annotated[
        Stamped[Celsius], field_meta(included_in_fmu=False)
    ]
    power: Annotated[Stamped[Watt], field_meta(included_in_fmu=False)]


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
    "BrightloopConverter",
    "ExchangerBoundary",
    "FlowBoundary",
    "HeatSource",
    "HvacExchanger",
    "OverpressureTemperatureBoundary",
    "Pcs",
    "PropulsionDrive",
    "ShorePowerConverter",
    "TemperatureBoundary",
    "Thruster",
    "Ugrid",
]
