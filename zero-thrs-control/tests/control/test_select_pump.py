def test_select_deselect_pump(thrusters_control):
    assert thrusters_control._active_pump is None 
    thrusters_control._activate_pump()
    assert thrusters_control._active_pump is thrusters_control._current_values.thrusters_pump1
    assert thrusters_control._current_values.thrusters_pump1.on
    assert thrusters_control._active_pump is not thrusters_control._current_values.thrusters_pump2
    thrusters_control._deactivate_pump()
    assert thrusters_control._most_recently_active_pump == "pump1"
    assert thrusters_control._active_pump is None
    thrusters_control._activate_pump()
    assert thrusters_control._active_pump is thrusters_control._current_values.thrusters_pump2

def test_select_pump_on_mode(thrusters_control):
    assert thrusters_control._active_pump is None 
    thrusters_control.to_recovery() 
    assert thrusters_control._active_pump is thrusters_control._current_values.thrusters_pump1
    assert thrusters_control._current_values.thrusters_pump1.on
    assert thrusters_control._active_pump is not thrusters_control._current_values.thrusters_pump2
    thrusters_control.to_idle() 
    assert thrusters_control._most_recently_active_pump == "pump1"
    assert thrusters_control._active_pump is None