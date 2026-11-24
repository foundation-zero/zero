from datetime import datetime

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.dc.control import DcControl
from thrs.control.modules.dc.io import DcControlValues
from thrs.control.modules.dc.state import DcParameters
from thrs.input_output.base import Stamped


def test_update_controls_reaches_aliased_sub_control_components():
    control = DcControl(DcParameters(), datetime.now, MachineStateLoggingServiceNoop())
    pump = control._current_values.dc_pump_aft
    switch = control._current_values.dc_switch_aft1

    control_values = DcControlValues.zero()
    control_values.dc_pump_aft.dutypoint = Stamped.stamp(0.42)
    control_values.dc_switch_aft1.setpoint = Stamped.stamp(1.0)

    control.update_controls(control_values)

    assert control._current_values.dc_pump_aft is pump
    assert control._current_values.dc_switch_aft1 is switch
    assert pump.dutypoint.value == 0.42
    assert switch.setpoint.value == 1.0
