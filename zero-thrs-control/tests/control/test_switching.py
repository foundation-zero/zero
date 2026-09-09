import logging
from datetime import datetime
from unittest import mock

import pytest

from tests.orchestration.simples import (
    SimpleControllerState,
    SimpleInOut,
    simple_advisory_values,
    simple_control_values,
    simple_non_advisory_values,
)
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
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
    """Actuated control values are not applied when in advisory mode"""
    switching_control = switching(manual_flow=1.0)
    control_values, _ = switching_control.control(
        simple_advisory_values(flow=9.0), simple_control_values(flow=7.0)
    )

    assert switching_control.manual
    assert control_values.go_with_the.flow.value == 1.0


def _mock_switching(
    initial_automatic: mock.Mock,
    factory: mock.Mock,
    time_fn=datetime.now,
    state_logger=None,
) -> Switching:
    initial_automatic.initial.return_value = (
        SimpleInOut.zero(),
        SimpleControllerState(),
    )
    return Switching(
        ManualControl(simple_control_values(flow=4.0)),
        initial_automatic,
        name="simple",
        automatic_factory=factory,
        time_fn=time_fn,
        state_logger=state_logger or MachineStateLoggingServiceNoop(),
    )


def test_manual_ticks_do_not_touch_automatic():
    automatic = mock.Mock()
    automatic.initial.return_value = (SimpleInOut.zero(), SimpleControllerState())
    switching_control = _mock_switching(automatic, mock.Mock(return_value=automatic))

    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=9.0)
    )

    assert control_values.go_with_the.flow.value == 4.0
    automatic.update_controls.assert_not_called()
    automatic.control.assert_not_called()
    assert controller_state == automatic.initial.return_value[1]


def test_manual_to_automatic_rebuilds_and_returns_first_control_tick():
    stale = mock.Mock()
    fresh = mock.Mock()
    fresh.control.return_value = (
        simple_control_values(flow=4.0),
        SimpleControllerState(),
    )
    factory = mock.Mock(return_value=fresh)
    time_fn = datetime.now
    state_logger = MachineStateLoggingServiceNoop()
    switching_control = _mock_switching(stale, factory, time_fn, state_logger)
    switching_control.control(simple_advisory_values(flow=9.0))
    assert switching_control.automatic_control is stale

    switching_control.switch_mode(AutomationMode(mode="automatic"))
    control_values, controller_state = switching_control.control(
        simple_advisory_values(flow=9.0)
    )

    # Switching to automatic gives a fresh control with persisted parameters
    assert switching_control.automatic_control is fresh
    factory.assert_called_once()
    assert factory.call_args[0][0] is stale.parameters
    assert factory.call_args[0][1] is time_fn
    assert factory.call_args[0][2] is state_logger
    stale.control.assert_not_called()
    fresh.control.assert_called_once()
    assert control_values.go_with_the.flow.value == 4.0
    assert controller_state is fresh.control.return_value[1]

    # Staying automatic ticks the same instance without rebuilding again
    switching_control.control(simple_advisory_values(flow=9.0))
    factory.assert_called_once()
    assert fresh.control.call_count == 2


def test_manual_to_automatic_ignores_manual(switching):
    switching_control = switching(manual_flow=99.0)
    stale = switching_control.automatic_control

    switching_control.switch_mode(AutomationMode(mode="automatic"))
    control_values, _ = switching_control.control(
        simple_advisory_values(flow=8.0), simple_control_values(flow=6.0)
    )

    assert switching_control.automatic_control is not stale
    assert control_values.go_with_the.flow.value == 8.0
    assert switching_control.manual_controls.go_with_the.flow.value == 99.0


def test_automatic_to_manual_snaps_to_actuated(switching):
    switching_control = switching(manual_flow=1.0)
    switching_control.switch_mode(AutomationMode(mode="automatic"))
    switching_control.control(simple_advisory_values(flow=8.0))

    switching_control.switch_mode(AutomationMode(mode="manual"))
    control_values, _ = switching_control.control(
        simple_advisory_values(flow=3.0), simple_control_values(flow=6.0)
    )

    assert switching_control.manual
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
