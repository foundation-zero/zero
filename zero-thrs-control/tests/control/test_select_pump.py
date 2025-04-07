from pytest import fixture

from control.modules.thrusters import ThrustersControl, ThrustersParameters


@fixture
def thrusters_control() -> ThrustersControl:
    return ThrustersControl(
        ThrustersParameters(
            cooling_mix_setpoint=40,
            recovery_thruster_flow=10,  # 50-S001 50-S002 per thruster
            cooling_thruster_flow=22,   # 50-S012 50-S013 per thruster
            max_temp=80,
            recovery_mix_setpoint=60,
        )
    )

def test_activate_pump(thrusters_control):
    assert thrusters_control._active_pump is None
    thrusters_control._activate_pump()
    assert thrusters_control._active_pump is thrusters_control._current_values.thrusters_pump_1
    assert thrusters_control._current_values.thrusters_pump_1.on
    assert thrusters_control._active_pump is not thrusters_control._current_values.thrusters_pump_2
    thrusters_control._deactivate_pump()
    assert thrusters_control._most_recently_active_pump == "pump1"
    assert thrusters_control._active_pump is None
    thrusters_control._activate_pump()
    assert thrusters_control._active_pump is thrusters_control._current_values.thrusters_pump_2

def test_activate_pump_on_mode(thrusters_control):
    assert thrusters_control._active_pump is None
    thrusters_control.to_recovery()
    assert thrusters_control._active_pump is thrusters_control._current_values.thrusters_pump_1
    assert thrusters_control._current_values.thrusters_pump_1.on
    assert thrusters_control._active_pump is not thrusters_control._current_values.thrusters_pump_2
    thrusters_control.to_idle()
    assert thrusters_control._most_recently_active_pump == "pump1"
    assert thrusters_control._active_pump is None
