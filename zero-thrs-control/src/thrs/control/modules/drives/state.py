from typing import Annotated

from thrs.classes.control import ControlMode
from thrs.control.modules.drives.io import DrivesControlValues
from thrs.control.switching import ControlState
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import Celsius, LMin, Tuning


class DrivesControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"

    @property
    def is_shorepower(self) -> bool:
        return self.mode == "shorepower"

    @property
    def is_propulsion(self) -> bool:
        return self.mode == "propulsion"


class DrivesParameters(ThrsValues):
    shorepower_maximum_supply_temperature: Celsius = 35
    propulsion_maximum_supply_temperature: Celsius = 60
    recovery_temperature: Celsius = 50
    shorepower_flow_setpoint: LMin = 20
    propulsion_drives_flow_setpoint: LMin = 30
    pump_tuning: Tuning = (0.01, 0.001, 0)
    recovery_mix_tuning: Tuning = (-0.1, -0.0005, 0)
    heat_dump_tuning: Tuning = (0.05, 0.01, 0)
    aft_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    fwd_flow_balance_tuning: Tuning = (0.01, 0.001, 0)


class DrivesControllerState(
    ControlState[DrivesControlValues, DrivesParameters, DrivesControlMode]
):
    drives_heat_dump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    drives_recovery_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    drives_pump_controller_shorepower: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    drives_pump_controller_propulsion: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    drives_aft_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    drives_fwd_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
