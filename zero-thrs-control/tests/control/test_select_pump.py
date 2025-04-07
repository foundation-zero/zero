from pytest import fixture

from control.modules.thrusters import ThrustersControl, ThrustersParameters


@fixture
def thrusters_control() -> ThrustersControl:
    return ThrustersControl(
        ThrustersParameters(
            cooling_mix_setpoint=40,
            cooling_pump_dutypoint=0.9,
            recovery_pump_dutypoint=0.5,
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
