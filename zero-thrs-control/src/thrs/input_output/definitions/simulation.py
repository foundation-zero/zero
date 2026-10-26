from datetime import UTC, datetime
from typing import Annotated

from pydantic import computed_field

from thrs.input_output.base import Stamped, ThrsValues, computed_meta, field_meta
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    LMin,
    OnOff,
    Overpressure,
    PcsMode,
    Watt,
)


def unset[T](value: T) -> Stamped[T]:
    return Stamped(value=value, timestamp=datetime.fromtimestamp(0, UTC))


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


class ActiveHeatSource(HeatSource):
    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def active(self) -> Stamped[OnOff]:
        return Stamped.combine(self.heat_flow, value=self.heat_flow.value > 0)


class Thruster(ActiveHeatSource):
    # TODO: add the pcs mode field
    pass


class PropulsionDrive(ActiveHeatSource):
    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def temp_power_stage(self) -> Stamped[Celsius]:
        return unset(0.0)

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def power(self) -> Stamped[Watt]:
        return unset(0.0)


class Ugrid(ActiveHeatSource):
    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def temp_power_stage(self) -> Stamped[Celsius]:
        return unset(0.0)

    @computed_field(json_schema_extra=computed_meta(included_in_fmu=False))
    @property
    def power(self) -> Stamped[Watt]:
        return unset(0.0)


def brightloop_converter(brightloop: ActiveHeatSource) -> sensor.BrightloopConverter:
    return sensor.BrightloopConverter(
        active=brightloop.active,
        cell01_temperature1=unset(0.0),
        cell01_temperature2=unset(0.0),
        cell02_temperature1=unset(0.0),
        cell02_temperature2=unset(0.0),
        power=unset(0.0),
    )


def shore_power_converter(
    shore_power: ActiveHeatSource,
) -> sensor.ShorePowerConverter:
    return sensor.ShorePowerConverter(
        active=shore_power.active,
        esi_transformer_temperature=unset(0.0),
        esi_igbt_min_temperature=unset(0.0),
        esi_igbt_max_temperature=unset(0.0),
        power=unset(0.0),
    )


class Pcs(ThrsValues):
    mode: Annotated[
        Stamped[PcsMode],
        field_meta(included_in_fmu=False),
    ]


class AdsorptionChiller(ThrsValues):
    free_cooling: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]


__all__ = [
    "ActiveHeatSource",
    "AdsorptionChiller",
    "Boundary",
    "ExchangerBoundary",
    "FlowBoundary",
    "HeatSource",
    "HvacExchanger",
    "OverpressureTemperatureBoundary",
    "Pcs",
    "PropulsionDrive",
    "TemperatureBoundary",
    "Thruster",
    "Ugrid",
]
