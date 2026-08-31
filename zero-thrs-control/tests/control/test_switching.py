from datetime import datetime

from tests.orchestration.simples import SimpleControl, SimpleInOut, SimpleParameters
from thrs.control.manual import ManualControl
from thrs.control.switching import (
    AutomationMode,
    Switching,
    SwitchingControlMode,
)


def test_switching_control():
    manual_control_values = SimpleInOut.zero()
    manual_control_values.go_with_the.flow.value = 42.0
    manual_control = ManualControl(manual_control_values)
    automated_control = SimpleControl(SimpleParameters.zero(), datetime.now)
    switching_control = Switching(manual_control, automated_control)

    control_values, controller_state = switching_control.initial()

    assert switching_control.mode == SwitchingControlMode(automatic_mode=None)
    assert not switching_control.automatic
    assert controller_state

    control_values, controller_state = switching_control.control(SimpleInOut.zero())
    assert controller_state
    assert control_values.go_with_the.flow.value == 42.0

    switching_control.switch_mode(AutomationMode(mode="automatic"))
    control_values, controller_state = switching_control.control(SimpleInOut.zero())

    assert switching_control.automatic
    assert controller_state
    assert control_values.go_with_the.flow.value == 0.0
