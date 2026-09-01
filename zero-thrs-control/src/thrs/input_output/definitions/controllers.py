from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import PvtMode, Seconds, TankState


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


class PvtControllerValues(ThrsValues):
    mode: Stamped[PvtMode]


__all__ = ["PidControllerValues", "PvtControllerValues", "TanksControllerValues"]
