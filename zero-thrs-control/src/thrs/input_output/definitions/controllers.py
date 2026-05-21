from thrs.control.modules.boilers import TankState
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import Seconds


class TanksControllerValues(ThrsValues):
    tank1_state: Stamped[TankState]
    tank2_state: Stamped[TankState]
    tank3_state: Stamped[TankState]
    time_to_fill: Stamped[Seconds | None]
