from enum import Enum

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import Celsius, Ratio, Seconds, TankState, Watt


class PcmChargingState(Enum):
    IDLE = "idle"
    CHARGING = "charging"
    DISCHARGING = "discharging"


PCM_CHARGING_DEADBAND: Watt = 100
PCM_CHARGE_FULL_TEMP: Celsius = 51  # TODO
PCM_CHARGE_EMPTY_TEMP: Celsius = 51  # TODO


class PidControllerValues(
    ThrsValues
):  # Not using generics here for strawberry compatibility.
    setpoint: Stamped[float]
    measurement: Stamped[float | None]
    output: Stamped[float | None]
    error: Stamped[float | None]
    enabled: Stamped[bool]
    tuning: Stamped[tuple[float, float, float]]
    components: Stamped[tuple[float, float, float]]


class TanksControllerValues(ThrsValues):
    tank1_state: Stamped[TankState]
    tank2_state: Stamped[TankState]
    tank3_state: Stamped[TankState]
    time_to_fill: Stamped[Seconds | None]
    time_to_hot: Stamped[Seconds | None]


class ChargeControllerValues(ThrsValues):
    charge: Stamped[Ratio]
    charging_state: Stamped[PcmChargingState]


__all__ = [
    "ChargeControllerValues",
    "PidControllerValues",
    "TanksControllerValues",
]
