from datetime import datetime

from input_output.definitions.control import Valve
from input_output.modules.thrusters import ThrustersSensorValues


def test_state_machine(control):
    sensor_values = ThrustersSensorValues.zero()
    control_values = control.control(sensor_values, datetime.now()).values
    assert control.state == "idle"
    assert not control_values.thrusters_pump_1.on.value

    control.to_recovery()
    control_values = control.control(sensor_values, datetime.now()).values
    assert control.state == "recovery"
    assert control_values.thrusters_shutoff_recovery.setpoint.value == Valve.OPEN
    assert control_values.thrusters_pump_1.on.value

    sensor_values.thrusters_temperature_supply.temperature.value = 100
    control_values = control.control(sensor_values, datetime.now()).values
    assert control.state == "cooling"
    assert control_values.thrusters_pump_1.on.value
    assert control_values.thrusters_shutoff_recovery.setpoint.value == Valve.CLOSED
