from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated, Self, cast

from thrs.input_output.base import Stamped, ThrsValues, field_meta
from thrs.input_output.definitions import control
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    Charged,
    Degree,
    DeltaT,
    Empty,
    Hz,
    Joule,
    Liter,
    LMin,
    NoError,
    OnOff,
    Operating,
    OptionalCelsius,
    PcsMode,
    Ratio,
    Seconds,
    Watt,
)


class FlowSensor(ThrsValues):
    flow: Stamped[LMin]
    temperature: Stamped[Celsius]
    quantity: Annotated[Stamped[Liter], field_meta(included_in_fmu=False)] = (
        Stamped(  # TODO: Remove default
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        )
    )


class Pump(ThrsValues):
    dutypoint: Annotated[Stamped[Ratio], field_meta(included_in_fmu=False)]
    on: Annotated[Stamped[OnOff], field_meta(included_in_fmu=False)]
    speed: Stamped[Hz]
    op_time: Stamped[Seconds] = Stamped(  # TODO: Remove default
        value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
    )
    flow: Stamped[LMin]
    pressure: Annotated[Stamped[Bar], field_meta(included_in_fmu=False)] = (
        Stamped(  # TODO: Remove default
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        )
    )
    energy_consumption: Annotated[Stamped[Joule], field_meta(included_in_fmu=False)] = (
        Stamped(  # TODO: Remove default
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        )
    )

    power_input: Annotated[Stamped[Watt], field_meta(included_in_fmu=False)] = (
        Stamped(  # TODO: Remove default
            value=0.0, timestamp=datetime.fromtimestamp(0, UTC)
        )
    )


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

    @classmethod
    def from_weighted_sensors(
        cls,
        weights: Sequence[Stamped[Ratio | LMin]],
        sensors: Sequence[TemperatureSensor],
        default_if_zero_weight: Celsius | None = None,
    ):
        stamps = [sensor.temperature for sensor in sensors]

        return CalculatedTemperature(
            temperature=weighted_combined_measurement(
                weights,
                stamps,
                default_if_zero_weight,
            ),
        )


class CalculatedFlow(ThrsValues):
    flow: Stamped[LMin]

    @classmethod
    def from_weighted_sensors(
        cls,
        weights: Sequence[Stamped[Ratio | LMin]],
        sensors: Sequence[FlowSensor | Self],
        default_if_zero_weight: LMin,
    ):
        stamps = [sensor.flow for sensor in sensors]

        return CalculatedFlow(
            flow=weighted_combined_measurement(
                weights,
                stamps,
                default_if_zero_weight,
            ),
        )

    @classmethod
    def from_summed_sensors(
        cls,
        *sensors: FlowSensor | Self,
    ):
        stamps = [sensor.flow for sensor in sensors]

        return CalculatedFlow(
            flow=Stamped.combine(*stamps, value=sum(sensor.value for sensor in stamps))
        )


class TemperatureDelta(ThrsValues):
    delta_t: Stamped[DeltaT]

    @classmethod
    def from_temperature_sensors(
        cls, temperature_supply: Stamped[Celsius], temperature_return: Stamped[Celsius]
    ) -> Self:
        delta_t = Stamped.combine(
            temperature_supply,
            temperature_return,
            value=temperature_return.value - temperature_supply.value,
        )
        return cls(delta_t=delta_t)


class HeatTransferDevice(ThrsValues):
    delta_t: Stamped[DeltaT]
    heat: Stamped[Watt]

    @classmethod
    def from_sensors(
        cls,
        temperature_supply: Stamped[Celsius],
        temperature_return: Stamped[Celsius],
        flow: Stamped[LMin],
        heat_transfer_conversion: float,
    ) -> Self:
        delta_t = Stamped.combine(
            temperature_supply,
            temperature_return,
            value=temperature_return.value - temperature_supply.value,
        )
        heat = Stamped.combine(
            delta_t, flow, value=flow.value * delta_t.value * heat_transfer_conversion
        )
        return cls(delta_t=delta_t, heat=heat)


class HvacExchanger(HeatTransferDevice):
    pass


class HeatPump(HeatTransferDevice):
    pass


class HeatExchanger(HeatTransferDevice):
    pass


class Valve(ThrsValues):
    position_rel: Stamped[Ratio]

    # Not used in control, only in frontend TODO: Remove when graphql api is split off
    position_abs: Annotated[Stamped[Degree], field_meta(included_in_fmu=False)] = (
        Stamped(value=0.0, timestamp=datetime.fromtimestamp(0, UTC))
    )


def valves_open_closed(
    open_valves: list[Valve] | None = None, closed_valves: list[Valve] | None = None
) -> bool:
    if open_valves is None:
        open_valves = []

    if closed_valves is None:
        closed_valves = []

    return all(
        valve.position_rel.value == control.Valve.OPEN for valve in open_valves
    ) and all(
        valve.position_rel.value < (control.Valve.CLOSED + 0.01)
        for valve in closed_valves
    )


def weighted_combined_measurement[
    Measurement: Celsius | LMin,
    Default: Celsius | LMin | None,
](
    weights: Sequence[Stamped[LMin | Ratio]],
    measurements: Sequence[Stamped[Measurement]],
    default_if_zero_weight: Default,
) -> Stamped[Default]:
    """Calculates a weighted average of measurements based on valve positions.

    Args:
        weights: Sequence of Stamped objects containing containing a Flow or Ratio.
        measurements: Sequence of Stamped measurement values corresponding to each
          valve.
        default_if_zero_weight: value to return if total valve position weight
          is 0 (or empty).

    Returns:
        The weighted combined measurement as a Stamped[float].

    Raises:
        ValueError: If the length of `weights` does not match `measurements`.
    """
    total_weight = sum(weight.value for weight in weights)

    if total_weight == 0:
        value = default_if_zero_weight
    else:
        weighted_sum = sum(
            weight.value * measurement.value
            for weight, measurement in zip(weights, measurements, strict=True)
        )
        value = cast(Default, weighted_sum / total_weight)

    return Stamped.combine(*weights, *measurements, value=value)


def inverse_ratio(ratio: Stamped["Ratio"]) -> Stamped["Ratio"]:
    return Stamped(
        value=1 - ratio.value,
        timestamp=ratio.timestamp,
    )


class PressureSensor(ThrsValues):
    pressure: Stamped[Bar]


class Thruster(ThrsValues):
    active: Stamped[OnOff]


class PropulsionDrive(ThrsValues):
    active: Stamped[OnOff]


class ShorePowerConverter(ThrsValues):
    active: Stamped[OnOff]


class Brightloop(ThrsValues):
    active: Stamped[OnOff]


class Ugrid(ThrsValues):
    active: Stamped[OnOff]


class Pcs(ThrsValues):
    mode: Stamped[PcsMode]


class Pcm(ThrsValues):
    charged: Stamped[Charged]


class LevelSwitch(ThrsValues):
    empty: Stamped[Empty]


# Leaving in commented fields as we might need these IOs in the future, but need to accomodate for them in the SimulationInputs or in the FMU first as they are currently not part of the FMU. For now, they are to be used as reference for the IOs that we might want to add in the future.
class AdsorptionChiller(ThrsValues):
    operating: Stamped[Operating]
    no_error: Stamped[NoError]
    free_cooling: Stamped[OnOff]
    # cooler_ventilator_speed: Annotated[
    #    Stamped[Ratio], field_meta(included_in_fmu=False)
    # ]
    # fault_cooler: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    temperature_hot_in: Stamped[Celsius]
    temperature_hot_out: Stamped[Celsius]
    temperature_waste_in: Stamped[Celsius]
    temperature_waste_out: Stamped[Celsius]
    temperature_cold_in: Stamped[Celsius]
    temperature_cold_out: Stamped[Celsius]
    # temperature_seawater: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    # available_temperature_hot: Annotated[
    #    Stamped[Celsius], field_meta(included_in_fmu=False)
    # ]
    # available_temperature_cold: Annotated[
    #    Stamped[Celsius], field_meta(included_in_fmu=False)
    # ]
    # available_temperature_waste: Annotated[Stamped[Celsius], field_meta(included_in_fmu=False)]
    # operating_hours_adsorption: Annotated[
    #    Stamped[Seconds], field_meta(included_in_fmu=False)
    # ]
    # operating_hours_free_cooling: Annotated[
    #    Stamped[Seconds], field_meta(included_in_fmu=False)
    # ]
    # cooling_energy: Annotated[Stamped[Joule], field_meta(included_in_fmu=False)]
    pump_speed_hot: Stamped[Ratio]
    pump_speed_cold: Stamped[Ratio]
    pump_speed_waste: Stamped[Ratio]
    # no_cold_flow: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    # freeze_protection: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    # low_cooling_capacity: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    # collective_fault_temperature_sensors: Annotated[
    #    Stamped[Error], field_meta(included_in_fmu=False)
    # ]
    # collective_fault_pumps: Annotated[Stamped[Error], field_meta(included_in_fmu=False)]
    # power_last_half_cycle: Annotated[Stamped[Watt], field_meta(included_in_fmu=False)]


class PowerSensor(ThrsValues):
    flow: Stamped[LMin]
    power: Stamped[Watt]
    delta_t: Stamped[DeltaT]
    temperature_warm: Stamped[Celsius]
    temperature_cold: Stamped[Celsius]


__all__ = [
    "AdsorptionChiller",
    "Brightloop",
    "CalculatedFlow",
    "CalculatedTemperature",
    "FlowSensor",
    "HeatExchanger",
    "HeatPump",
    "HeatTransferDevice",
    "HvacExchanger",
    "LevelSensor",
    "LevelSwitch",
    "Pcm",
    "Pcs",
    "PowerSensor",
    "PressureSensor",
    "PropulsionDrive",
    "Pump",
    "ShorePowerConverter",
    "TemperatureDelta",
    "TemperatureSensor",
    "Thruster",
    "Ugrid",
    "Valve",
]
