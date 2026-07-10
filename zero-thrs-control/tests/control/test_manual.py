from datetime import datetime

from tests.orchestration.simples import SimpleInOut
from thrs.control.manual import ManualControl
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.sensor import FlowSensor


def test_manual_control():
    control = ManualControl(SimpleInOut.zero(), datetime.now)
    assert control.control(SimpleInOut.zero())[0].go_with_the.flow.value == 0.0
    control.update_controls(
        SimpleInOut(
            go_with_the=FlowSensor(
                flow=Stamped.stamp(1.0), temperature=Stamped.stamp(2.0)
            )
        )
    )
    assert control.control(SimpleInOut.zero())[0].go_with_the.flow.value == 1.0
