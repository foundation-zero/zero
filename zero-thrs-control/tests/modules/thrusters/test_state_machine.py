from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.thrusters import ThrustersSensorValues


def test_state_machine(control):
    sensor_values = ThrustersSensorValues.zero()
    assert control.state == "idle"
    assert not control._current_control_values.thrusters_pump1.on.value

    control.to_warmup(sensor_values)
    assert control.state == "warmup"
    assert (
        control._current_control_values.thrusters_switch_recovery.setpoint.value
        == Valve.OPEN
    )
    assert control._current_control_values.thrusters_pump1.on.value

    control.to_cooling(sensor_values)
    assert control.state == "cooling"
    assert control._current_control_values.thrusters_pump1.on.value
    assert (
        control._current_control_values.thrusters_switch_recovery.setpoint.value
        == Valve.CLOSED
    )
