from enum import Enum

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import Seconds


class TankState(Enum):
    IN_USE = "in use"
    FILLING = "filling"
    BOOSTING = "boosting"
    DISABLED = "disabled"
    NEEDS_BOOST = "needs boost"
    NEEDS_FILL = "needs fill"
    STANDBY = "standby"


class TanksControllerValues(ThrsValues):
    tank1_state: Stamped[TankState]
    tank2_state: Stamped[TankState]
    tank3_state: Stamped[TankState]
    time_to_fill: Stamped[Seconds | None]


__all__ = ["TanksControllerValues"]
