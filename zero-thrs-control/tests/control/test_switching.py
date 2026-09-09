import logging
from unittest import mock

import pytest

from tests.orchestration.simples import (
    SimpleControllerState,
    SimpleInOut,
    simple_advisory_values,
    simple_control_values,
    simple_non_advisory_values,
)
from thrs.control.manual import ManualControl
from thrs.control.switching import (
    AutomationMode,
    Switching,
    SwitchingControlMode,
)


def test_switching_control(switching):
    switching_control = switching(manual_flow=42.0)

    control_values, controller_state = switching_control.initial()

    assert switching_control.mode == SwitchingControlMode(automatic_mode=None)
    assert not switching_control.automatic
    assert controller_state

    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=42.0)
    )
    assert controller_state
    assert control_values.go_with_the.flow.value == 42.0
    assert controller_state == switching_control.automatic_control.initial()[1]

    switching_control.switch_mode(AutomationMode(mode="automatic"))
    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=30.0)
    )

    assert switching_control.automatic
    assert controller_state
    assert control_values.go_with_the.flow.value == 30.0


@pytest.mark.parametrize(
    ("actuated_flow", "expected_flow"),
    [(7.0, 7.0), (None, 1.0)],
)
def test_non_advisory_forces_manual_and_tracks_actuated(
    switching, actuated_flow, expected_flow
):
    switching_control = switching(manual_flow=1.0)
    switching_control.switch_mode(AutomationMode(mode="automatic"))
    actuated = None if actuated_flow is None else simple_control_values(actuated_flow)

    control_values, _ = switching_control.control(
        simple_non_advisory_values(flow=9.0), actuated
    )

    assert switching_control.manual
    assert control_values.go_with_the.flow.value == expected_flow
    assert switching_control.manual_controls.go_with_the.flow.value == expected_flow


def test_advisory_restore_does_not_auto_engage(switching):
    switching_control = switching(manual_flow=1.0)
    switching_control.control(
        simple_advisory_values(flow=9.0), simple_control_values(flow=7.0)
    )

    control_values, _ = switching_control.control(simple_advisory_values(flow=9.0))

    assert switching_control.manual
    assert control_values.go_with_the.flow.value == 7.0


def test_manual_ticks_push_manual_output_to_automatic():
    automatic = mock.Mock()
    automatic.initial.return_value = (SimpleInOut.zero(), SimpleControllerState())
    switching_control = Switching(
        ManualControl(simple_control_values(flow=4.0)), automatic, name="simple"
    )

    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=9.0)
    )

    assert control_values.go_with_the.flow.value == 4.0
    automatic.update_controls.assert_called_once()
    tracked = automatic.update_controls.call_args[0][0]
    assert tracked.go_with_the.flow.value == 4.0
    assert controller_state == automatic.initial.return_value[1]


def test_first_automatic_step_uses_tracked_values():
    # Switching only owns the handover: manual output is pushed into automatic
    # on every manual tick, and the first automatic output passes through while
    # manual starts tracking it. Resuming from the pushed values is the
    # automatic control's own job.
    automatic = mock.Mock()
    automatic.initial.return_value = (SimpleInOut.zero(), SimpleControllerState())
    automatic.control.return_value = (
        simple_control_values(flow=4.0),
        SimpleControllerState(),
    )
    switching_control = Switching(
        ManualControl(simple_control_values(flow=4.0)), automatic, name="simple"
    )
    switching_control.control(simple_advisory_values(flow=9.0))

    switching_control.switch_mode(AutomationMode(mode="automatic"))
    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=9.0)
    )

    assert switching_control.automatic
    automatic.control.assert_called_once()
    assert control_values.go_with_the.flow.value == 4.0
    assert controller_state is automatic.control.return_value[1]
    assert switching_control.manual_controls.go_with_the.flow.value == 4.0


def test_automatic_to_manual_tracks_last_auto(switching):
    switching_control = switching(manual_flow=1.0)
    switching_control.switch_mode(AutomationMode(mode="automatic"))
    auto_sensor = simple_advisory_values(flow=8.0)
    switching_control.control(auto_sensor)

    switching_control.switch_mode(AutomationMode(mode="manual"))
    control_values, _ = switching_control.control(simple_advisory_values(flow=3.0))

    assert switching_control.manual
    assert control_values.go_with_the.flow.value == 8.0


@pytest.mark.parametrize("start_automatic", [True, False])
def test_advisory_disable_logs_warning_on_falling_edge_only(
    switching, caplog, start_automatic
):
    switching_control = switching(manual_flow=1.0)
    switching_control.control(simple_advisory_values(flow=1.0))
    if start_automatic:
        switching_control.switch_mode(AutomationMode(mode="automatic"))
        switching_control.control(simple_advisory_values(flow=8.0))

    with caplog.at_level(logging.WARNING, logger="thrs.control.switching"):
        control_values, _ = switching_control.control(
            simple_non_advisory_values(flow=2.0), simple_control_values(flow=6.0)
        )

    assert switching_control.manual
    assert control_values.go_with_the.flow.value == 6.0
    assert (
        sum("advisory was disabled for simple" in r.message for r in caplog.records)
        == 1
    )

    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="thrs.control.switching"):
        switching_control.control(
            simple_non_advisory_values(flow=2.0), simple_control_values(flow=6.0)
        )

    assert caplog.records == []
