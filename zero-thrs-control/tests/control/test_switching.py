import logging
from unittest import mock

import pytest

from tests.orchestration.simples import (
    SimpleControllerState,
    SimpleInOut,
    SimpleParameters,
    simple_advisory_values,
    simple_control_values,
    simple_non_advisory_values,
)
from thrs.control.state import AutomationMode
from thrs.control.switching import Switching


def test_switching_control(switching):
    switching_control = switching(manual_flow=42.0)

    controller_state = switching_control.idle_state()

    assert controller_state.automation_mode == AutomationMode(mode="manual")
    assert controller_state.control_mode is None

    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=42.0)
    )
    assert control_values.go_with_the.flow.value == 42.0
    assert controller_state == switching_control.automatic_control.initial()[
        1
    ].model_copy(update={"manual_values": switching_control.manual_controls})
    assert controller_state.automation_mode == AutomationMode(mode="manual")
    assert controller_state.parameters == SimpleParameters.zero()

    switching_control.switch_mode(AutomationMode(mode="automatic"))
    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=30.0)
    )

    assert controller_state.automation_mode == AutomationMode(mode="automatic")
    assert controller_state.control_mode == switching_control.automatic_control.mode
    assert controller_state.parameters == SimpleParameters.zero()
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

    control_values, controller_state = switching_control.control(
        simple_non_advisory_values(flow=9.0), actuated
    )

    assert controller_state.automation_mode == AutomationMode(mode="manual")
    assert control_values.go_with_the.flow.value == expected_flow
    assert switching_control.manual_controls.go_with_the.flow.value == expected_flow


def test_advisory_restore_does_not_auto_engage(switching):
    """Actuated control values are not applied when in advisory mode"""
    switching_control = switching(manual_flow=1.0)
    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=9.0), simple_control_values(flow=7.0)
    )

    assert controller_state.automation_mode == AutomationMode(mode="manual")
    assert control_values.go_with_the.flow.value == 1.0


def _mock_switching(automatic: mock.Mock) -> tuple[Switching, mock.Mock]:
    """A switching control whose automatic control is always `automatic`, and the
    factory that builds it, to count the builds."""
    automatic.initial.return_value = (
        SimpleInOut.zero(),
        SimpleControllerState(parameters=SimpleParameters()),
    )
    create_automatic = mock.Mock(return_value=automatic)
    switching_control = Switching(create_automatic, SimpleParameters(), name="simple")
    switching_control.update_manual_controls(simple_control_values(flow=4.0))
    return switching_control, create_automatic


def test_manual_ticks_do_not_touch_automatic():
    automatic = mock.Mock()
    switching_control, create_automatic = _mock_switching(automatic)

    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=9.0)
    )

    assert control_values.go_with_the.flow.value == 4.0
    assert automatic.control.call_count == 0
    assert create_automatic.call_count == 1
    assert controller_state == automatic.initial.return_value[1]


def test_manual_to_automatic_rebuilds_and_returns_first_control_tick():
    automatic = mock.Mock()
    automatic.control.return_value = (
        simple_control_values(flow=4.0),
        SimpleControllerState(parameters=SimpleParameters()),
    )
    switching_control, create_automatic = _mock_switching(automatic)
    switching_control.control(simple_advisory_values(flow=9.0))
    assert create_automatic.call_count == 1

    switching_control.switch_mode(AutomationMode(mode="automatic"))
    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=9.0)
    )

    # Switching to automatic builds a fresh control from the current parameters
    assert create_automatic.call_args_list == [
        mock.call(SimpleParameters()),
        mock.call(SimpleParameters()),
    ]
    assert automatic.control.call_count == 1
    assert control_values.go_with_the.flow.value == 4.0
    assert controller_state is automatic.control.return_value[1]

    # Staying automatic ticks the same control without building again
    switching_control.control(simple_advisory_values(flow=9.0))
    assert create_automatic.call_count == 2
    assert automatic.control.call_count == 2


def test_manual_to_automatic_ignores_manual(switching):
    switching_control = switching(manual_flow=99.0)

    switching_control.switch_mode(AutomationMode(mode="automatic"))
    control_values, _ = switching_control.control(
        simple_advisory_values(flow=8.0), simple_control_values(flow=6.0)
    )

    assert control_values.go_with_the.flow.value == 8.0
    assert switching_control.manual_controls.go_with_the.flow.value == 99.0


def test_automatic_to_manual_snaps_to_actuated(switching):
    switching_control = switching(manual_flow=1.0)
    switching_control.switch_mode(AutomationMode(mode="automatic"))
    switching_control.control(simple_advisory_values(flow=8.0))

    switching_control.switch_mode(AutomationMode(mode="manual"))
    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=3.0), simple_control_values(flow=6.0)
    )

    assert controller_state.automation_mode == AutomationMode(mode="manual")
    assert control_values.go_with_the.flow.value == 6.0
    assert switching_control.manual_controls.go_with_the.flow.value == 6.0

    # Staying manual keeps the current value, ignoring newer actuated values.
    control_values, _ = switching_control.control(
        simple_advisory_values(flow=3.0), simple_control_values(flow=9.0)
    )
    assert control_values.go_with_the.flow.value == 6.0


def test_manual_stays_isolated_from_actuated(switching):
    switching_control = switching(manual_flow=1.0)
    for actuated_flow in (7.0, 8.0):
        control_values, _ = switching_control.control(
            simple_advisory_values(flow=9.0),
            simple_control_values(flow=actuated_flow),
        )
        assert control_values.go_with_the.flow.value == 1.0
    assert switching_control.manual_controls.go_with_the.flow.value == 1.0


def test_non_advisory_staying_keeps_echoing(switching):
    switching_control = switching(manual_flow=1.0)
    for expected_flow in (6.0, 7.0):
        control_values, _ = switching_control.control(
            simple_non_advisory_values(flow=2.0),
            simple_control_values(flow=expected_flow),
        )
        assert control_values.go_with_the.flow.value == expected_flow
    assert switching_control.manual_controls.go_with_the.flow.value == 7.0


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
        control_values, controller_state = switching_control.control(
            simple_non_advisory_values(flow=2.0), simple_control_values(flow=6.0)
        )

    assert controller_state.automation_mode == AutomationMode(mode="manual")
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
