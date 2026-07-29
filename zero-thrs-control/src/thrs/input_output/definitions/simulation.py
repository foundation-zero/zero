from typing import Annotated

from pydantic.json_schema import SkipJsonSchema

from thrs.input_output.base import Stamped, StampedDf, ThrsValues, field_meta
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    LMin,
    OnOff,
    Overpressure,
    PcsMode,
    Watt,
)

type Stamp[T] = Stamped[T] | SkipJsonSchema[StampedDf[T]]


class HeatSource(ThrsValues):
    heat_flow: Stamp[Watt]


class HvacExchanger(ThrsValues):
    heat_flow: Stamp[Watt]
    maximum_temperature: Stamp[Celsius]


class Boundary(ThrsValues):
    temperature: Stamp[Celsius]
    flow: Stamp[LMin]


class ExchangerBoundary(ThrsValues):
    flow: Stamp[LMin]
    temperature_supply: Stamp[Celsius]
    temperature_return: Stamp[Celsius]


class OverpressureTemperatureBoundary(ThrsValues):
    temperature: Stamp[Celsius]
    overpressure: Stamp[Overpressure]


class TemperatureBoundary(ThrsValues):
    temperature: Stamp[Celsius]


class PressureBoundary(ThrsValues):
    pressure: Stamp[Bar]


class FlowBoundary(ThrsValues):
    flow: Stamp[LMin]


class Thruster(HeatSource):
    active: Annotated[Stamp[bool], field_meta(included_in_fmu=False)]


class PropulsionDrive(HeatSource):
    active: Annotated[Stamp[bool], field_meta(included_in_fmu=False)]


class Converter(HeatSource):
    active: Annotated[Stamp[bool], field_meta(included_in_fmu=False)]


class Pcs(ThrsValues):
    mode: Annotated[
        Stamp[PcsMode],
        field_meta(included_in_fmu=False),
    ]


class AdsorptionChiller(ThrsValues):
    free_cooling: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]


__all__ = [
    "Boundary",
    "FlowBoundary",
    "HeatSource",
    "Pcs",
    "TemperatureBoundary",
    "Thruster",
]
