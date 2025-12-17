from typing import Annotated, ClassVar
from thrs.input_output.base import Stamped, ThrsValues, field_meta
from thrs.input_output.definitions.units import (
    Celsius,
    FahrenheitMode,
    FreeCoolingMode,
    Kelvin,
    OnOff,
    Ratio,
    TankControlMode,
)


class Pump(ThrsValues):
    dutypoint: Stamped[Ratio]
    on: Stamped[OnOff]


class Valve(ThrsValues):
    CLOSED: ClassVar = 0.0
    OPEN: ClassVar = 1.0

    SWITCH_BRANCH: ClassVar = 0.0
    SWITCH_STRAIGHT: ClassVar = 1.0

    MIXING_B_TO_AB: ClassVar = 0.0
    MIXING_A_TO_AB: ClassVar = 1.0

    setpoint: Stamped[Ratio]
    """
    The setpoint of the valve, represented as a ratio between 0 and 1.

    Valve Conventions:
        - 2-Way Switch or Needle Valve:
            - 0: Closed
            - 1: Open
        - 3-Way Switch Valve:
            - 0: Branch (flow from the other inlet to the outlet)
            - 1: Straight (flow from one inlet to the outlet)
        - Mixing Valve:
            - 0: Flow from B to AB
            - 1: Flow from A to AB
    """


class Pcm(ThrsValues):
    on: Stamped[OnOff]


class Fahrenheit(ThrsValues):
    enable: Stamped[OnOff]
    mode: Stamped[FahrenheitMode]
    cooling_setpoint: Stamped[Celsius]
    free_cooling_mode: Stamped[FreeCoolingMode]
    temperature_seawater: Stamped[Celsius]
    temperature_hot: Stamped[Celsius]
    temperature_cold: Stamped[Celsius]
    cold_threshold: Stamped[Celsius]
    hot_threshold: Stamped[Celsius]
    cold_hysteresis: Stamped[Kelvin]
    hot_hysteresis: Stamped[Kelvin]
    tank_control_mode: Annotated[
        Stamped[TankControlMode], field_meta(included_in_fmu=False)
    ]


class HeatPump(ThrsValues):
    on: Stamped[OnOff]
    temperature_setpoint: Stamped[Celsius]


__all__ = ["Pump", "Valve", "Pcm", "Fahrenheit", "HeatPump"]
