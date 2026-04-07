from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import (
    Bar,
    Celsius,
    Charged,
    Hz,
    Kelvin,
    LMin,
    Liter,
    NoError,
    OnOff,
    Operating,
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
    active: Stamped[OnOff]


class PropulsionDrive(ThrsValues):
    active: Stamped[OnOff]


class ShorePowerConverter(ThrsValues):
    active: Stamped[OnOff]


class Pcs(ThrsValues):
    mode: Stamped[PcsMode]


class Pcm(ThrsValues):
    charged: Stamped[Charged]


# Leaving in commented fields as we might need these IOs in the future, but need to accomodate for them in the SimulationInputs or in the FMU first as they are currently not part of the FMU. For now, they are to be used as reference for the IOs that we might want to add in the future.
class Fahrenheit(ThrsValues):
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
    #    Stamped[seconds], field_meta(included_in_fmu=False)
    # ]
    # operating_hours_free_cooling: Annotated[
    #    Stamped[seconds], field_meta(included_in_fmu=False)
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
