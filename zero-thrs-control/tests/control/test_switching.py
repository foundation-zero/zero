from datetime import datetime
from tests.orchestration.simples import SimpleControl, SimpleInOut, SimpleParameters
from thrs.control.manual import ManualControl
from thrs.control.switching import SwitchingControl


def test_switching_control():
    manual_control_values = SimpleInOut.zero()
    manual_control_values.go_with_the.flow.value = 42.0
    manual_control = ManualControl(manual_control_values, datetime.now)
    automated_control = SimpleControl(SimpleParameters.zero(), datetime.now)
    switching_control = SwitchingControl(manual_control, automated_control)
    assert switching_control.mode == "manual"
    assert (
        switching_control.control(SimpleInOut.zero()).values.go_with_the.flow.value
        == 42.0
    )
    switching_control.switch_mode("automatic")
    assert switching_control.mode == "automatic"
    assert (
        switching_control.control(SimpleInOut.zero()).values.go_with_the.flow.value
        == 0.0
    )
