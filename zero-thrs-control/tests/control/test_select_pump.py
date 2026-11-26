import pytest

from thrs.control.modules.thrusters.io import ThrustersSensorValues
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.sensor import Pcs
from thrs.input_output.definitions.units import PcsMode


def test_activate_pump(thrusters_control):
    assert thrusters_control._active_pump is None
    thrusters_control._activate_pump(ThrustersSensorValues.initial())
    assert (
        thrusters_control._active_pump
        is thrusters_control._current_control_values.thrusters_pump1
    )
    assert thrusters_control._current_control_values.thrusters_pump1.on
    assert (
        thrusters_control._active_pump
        is not thrusters_control._current_control_values.thrusters_pump2
    )
    thrusters_control._deactivate_pump(ThrustersSensorValues.initial())
    assert thrusters_control._most_recently_active_pump == "pump1"
    assert thrusters_control._active_pump is None
    thrusters_control._activate_pump(ThrustersSensorValues.initial())
    assert (
        thrusters_control._active_pump
        is thrusters_control._current_control_values.thrusters_pump2
    )


def test_activate_pump_on_mode(thrusters_control):
    pcs_off = ThrustersSensorValues.initial()
    pcs_propulsion = pcs_off.model_copy(
        update={"thrusters_pcs": Pcs(mode=Stamped.stamp(PcsMode.PROPULSION))}
    )

    assert thrusters_control._active_pump is None
    thrusters_control.control(pcs_propulsion)  # idle → warmup
    assert (
        thrusters_control._active_pump
        is thrusters_control._current_control_values.thrusters_pump1
    )
    assert thrusters_control._current_control_values.thrusters_pump1.on
    assert (
        thrusters_control._active_pump
        is not thrusters_control._current_control_values.thrusters_pump2
    )
    thrusters_control.control(pcs_off)  # warmup → cooldown
    thrusters_control.control(pcs_off)  # cooldown → idle
    assert thrusters_control._most_recently_active_pump == "pump1"
    assert thrusters_control._active_pump is None


def test_error_in_mode_change_raises(thrusters_control):
    pcs_propulsion = ThrustersSensorValues.initial().model_copy(
        update={"thrusters_pcs": Pcs(mode=Stamped.stamp(PcsMode.PROPULSION))}
    )
    thrusters_control._activate_pump(ThrustersSensorValues.initial())

    with pytest.raises(Warning, match="A pump was already active upon selecting"):
        thrusters_control.control(pcs_propulsion)  # idle → warmup activates a pump
