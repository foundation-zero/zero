from typing import Annotated, ClassVar

from pydantic import field_validator

from thrs.input_output.base import Stamped, ThrsValues, field_meta
from thrs.input_output.definitions.units import (
    AdsorptionChillerMode,
    Celsius,
    DeltaT,
    FreeCoolingMode,
    OnOff,
    Ratio,
    TankControlMode,
)


class Pump(ThrsValues):
    dutypoint: Stamped[Ratio]
    on: Stamped[OnOff]

    # TODO: Remove once marpower fixes this on their side
    @field_validator("dutypoint")
    @classmethod
    def correct_marpower_range(cls, value: Stamped[Ratio]) -> Stamped[Ratio]:
        value.value *= 100

        return value


class Valve(ThrsValues):
    CLOSED: ClassVar = 0.0
    OPEN: ClassVar = 1.0

    SWITCH_B: ClassVar = 0.0
    SWITCH_A: ClassVar = 1.0

    MIXING_B_TO_AB: ClassVar = 0.0
    MIXING_A_TO_AB: ClassVar = 1.0

    setpoint: Stamped[Ratio]
    """
    The setpoint of the valve, represented as a ratio between 0 and 1.

    Valve Conventions:
        - 2-Way Switch or Flow Control Valve:
            - 0: Closed
            - 1: Open
        - 3-Way Switch Valve:
            - 0: Flow from AB to B
            - 1: Flow from AB to A
        - Mixing Valve:
            - 0: Flow from B to AB
            - 1: Flow from A to AB
    """


class Pcm(ThrsValues):
    on: Stamped[OnOff]


class AdsorptionChiller(ThrsValues):
    enable: Stamped[OnOff]
    mode: Stamped[AdsorptionChillerMode]
    cooling_setpoint: Stamped[Celsius]
    free_cooling_mode: Annotated[
        Stamped[FreeCoolingMode], field_meta(included_in_fmu=False)
    ]
    available_seawater_temperature: Annotated[
        Stamped[Celsius], field_meta(included_in_fmu=False)
    ]
    available_hot_temperature: Stamped[Celsius]
    available_cold_temperature: Stamped[Celsius]
    cold_minimum: Stamped[Celsius]
    hot_minimum: Stamped[Celsius]
    cold_hysteresis: Stamped[DeltaT]
    hot_hysteresis: Stamped[DeltaT]
    tank_control_mode: Annotated[
        Stamped[TankControlMode], field_meta(included_in_fmu=False)
    ]


class HeatPump(ThrsValues):
    on: Stamped[OnOff]
    temperature_setpoint: Stamped[Celsius]


__all__ = ["AdsorptionChiller", "HeatPump", "Pcm", "Pump", "Valve"]
