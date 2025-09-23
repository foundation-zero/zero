from thrs.control.modules.thrusters import ThrustersControl
from thrs.input_output.modules.thrusters import ThrustersSensorValues


def test_all_valves_active(thrusters_control: ThrustersControl):
    thrusters_control._activate_pump(ThrustersSensorValues.zero())

    thrusters_control._flow_balance_controller.enable([True, True])
    thrusters_control._flow_balance_controller.set_setpoints([20.0, 30.0])
    thrusters_control._flow_balance_controller.set_pump(thrusters_control._active_pump)

    thrusters_control._flow_balance_controller([10.0, 31.0], thrusters_control._time)

    assert (
        thrusters_control._current_values.thrusters_flowcontrol_aft.setpoint.value > 0
    )
    assert (
        thrusters_control._current_values.thrusters_flowcontrol_fwd.setpoint.value < 1
    )
    assert thrusters_control._current_values.thrusters_pump_1.dutypoint.value > 0


def test_no_valves_active(thrusters_control: ThrustersControl):
    thrusters_control._activate_pump(ThrustersSensorValues.zero())

    thrusters_control._flow_balance_controller.set_setpoints([20.0, 30.0])
    thrusters_control._flow_balance_controller.set_pump(thrusters_control._active_pump)

    thrusters_control._flow_balance_controller([10.0, 31.0], thrusters_control._time)

    assert (
        thrusters_control._current_values.thrusters_flowcontrol_aft.setpoint.value == 0
    )
    assert (
        thrusters_control._current_values.thrusters_flowcontrol_fwd.setpoint.value == 0
    )
    assert thrusters_control._current_values.thrusters_pump_1.dutypoint.value == 0


def test_one_valve_active(thrusters_control: ThrustersControl):
    thrusters_control._activate_pump(ThrustersSensorValues.zero())

    thrusters_control._flow_balance_controller.enable([False, True])

    thrusters_control._flow_balance_controller.set_setpoints([20.0, 30.0])
    thrusters_control._flow_balance_controller.set_pump(thrusters_control._active_pump)

    thrusters_control._flow_balance_controller([0, 29.0], thrusters_control._time)

    assert (
        thrusters_control._current_values.thrusters_flowcontrol_aft.setpoint.value == 0
    )
    assert (
        thrusters_control._current_values.thrusters_flowcontrol_fwd.setpoint.value > 0
    )
    assert thrusters_control._pump_flow_controller.setpoint == 30.0
    assert thrusters_control._current_values.thrusters_pump_1.dutypoint.value > 0
