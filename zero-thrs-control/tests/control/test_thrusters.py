from control.modules.thrusters import ThrustersControl, ThrustersSetpoints
from input_output.base import Stamped


def test_select_pump_from_start():
    control = ThrustersControl(ThrustersSetpoints(cooling_mix_setpoint=40))
    pump = control.select_pump()
    assert pump is control._current_values.thrusters_pump1
    assert pump is not control._current_values.thrusters_pump2


def test_select_pump1_active():
    control = ThrustersControl(ThrustersSetpoints(cooling_mix_setpoint=40))
    control._current_values.thrusters_pump1.on = Stamped.stamp(True)
    pump = control.select_pump()
    assert pump is control._current_values.thrusters_pump1


def test_select_pump2_active():
    control = ThrustersControl(ThrustersSetpoints(cooling_mix_setpoint=40))
    control._current_values.thrusters_pump2.on = Stamped.stamp(True)
    pump = control.select_pump()
    assert pump is control._current_values.thrusters_pump2


def test_select_pump1_most_recently_used():
    control = ThrustersControl(ThrustersSetpoints(cooling_mix_setpoint=40))
    _first = control.select_pump()
    second = control.select_pump()
    assert second is control._current_values.thrusters_pump2


def test_select_pump2_most_recently_used():
    control = ThrustersControl(ThrustersSetpoints(cooling_mix_setpoint=40))
    _first = control.select_pump()
    _second = control.select_pump()
    third = control.select_pump()
    assert third is control._current_values.thrusters_pump1
