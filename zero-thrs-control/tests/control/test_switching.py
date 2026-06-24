from datetime import datetime

from tests.orchestration.simples import SimpleControl, SimpleInOut, SimpleParameters
from thrs.control.manual import ManualControl
from thrs.control.switching import SwitchingControl, SwitchingControllerValues


def test_switching_control():
    manual_control_values = SimpleInOut.zero()
    manual_control_values.go_with_the.flow.value = 42.0
    manual_control = ManualControl(manual_control_values, datetime.now)
    automated_control = SimpleControl(SimpleParameters.zero(), datetime.now)
    switching_control = SwitchingControl(manual_control, automated_control)

    control_values, controller_values = switching_control.initial()

    assert controller_values == SwitchingControllerValues(automatic_mode=None)

    control_values, controller_values = switching_control.control(SimpleInOut.zero())

    assert controller_values.automatic_mode is None
    assert control_values.go_with_the.flow.value == 42.0

    switching_control.switch_mode("automatic")
    control_values, controller_values = switching_control.control(SimpleInOut.zero())

    assert controller_values.automatic_mode is not None
    assert control_values.go_with_the.flow.value == 0.0
