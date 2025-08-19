
from input_output.definitions.control import Valve
from input_output.modules.thrusters import ThrustersSensorValues


def test_state_machine(control):
    sensor_values = ThrustersSensorValues.zero()
    assert control.state == "idle"
    assert not control._current_values.thrusters_pump_1.on.value

    control.to_recovery(sensor_values)
    assert control.state == "recovery"
    assert control._current_values.thrusters_shutoff_recovery.setpoint.value == Valve.OPEN
    assert control._current_values.thrusters_pump_1.on.value

    control.to_cooling(sensor_values)
    assert control.state == "cooling"
    assert control._current_values.thrusters_pump_1.on.value
    assert control._current_values.thrusters_shutoff_recovery.setpoint.value == Valve.CLOSED

#TODO: add state machine test with actual controls
