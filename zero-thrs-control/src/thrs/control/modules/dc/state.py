from typing import Annotated

from thrs.classes.control import ControlMode
from thrs.control.modules.dc.converters import ConvertersControlMode
from thrs.control.modules.dc.io import DcControlValues
from thrs.control.state import ControlState
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import Celsius, LMin, Tuning


class DcControlMode(ControlMode):
    brightloops_aft: ConvertersControlMode
    brightloops_fwd: ConvertersControlMode
    ugrids: ConvertersControlMode


class DcParameters(ThrsValues):
    maximum_supply_temperature: Celsius = 63
    recovery_temperature: Celsius = 60
    brightloop_flow_setpoint: LMin = 5
    ugrid_flow_setpoint: LMin = 15
    brightloop_return_temperature: Celsius = 60
    ugrid_return_temperature: Celsius = 60
    heat_dump_tuning: Tuning = (0.01, 0.001, 0.001)
    recovery_mix_tuning: Tuning = (-0.01, -0.001, -0.01)
    brightloops_fwd_mix_tuning: Tuning = (-0.01, -0.001, -0.01)
    brightloops_aft_mix_tuning: Tuning = (-0.01, -0.001, -0.01)
    ugrids_mix_tuning: Tuning = (-0.01, -0.001, -0.01)
    brightloops_fwd_pump_tuning: Tuning = (0.01, 0.001, 0)
    brightloops_aft_pump_tuning: Tuning = (0.01, 0.001, 0)
    ugrids_pump_tuning: Tuning = (0.01, 0.001, 0)


class DcControllerState(ControlState[DcControlValues, DcParameters, DcControlMode]):
    dc_heat_dump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dc_recovery_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dc_brightloops_aft_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dc_brightloops_aft_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dc_brightloops_fwd_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dc_brightloops_fwd_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dc_ugrids_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dc_ugrids_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
