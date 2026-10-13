from unittest.mock import Mock

from transitions import Machine

from tests.classes.machine_state_logger.conftest import (
    DummyControl,
    added_model,
    make_states,
    make_transitions,
)
from thrs.classes.machine_state_logger import MachineStateLoggingService
from thrs.db.models.machine_state import MachineStateTransition


def test_create_logged_state_machine_returns_machine(
    service: MachineStateLoggingService,
) -> None:
    control = DummyControl()

    machine = service.create_logged_state_machine(
        control, make_transitions(), make_states(), initial="idle"
    )

    assert isinstance(machine, Machine)
    assert control.state == "idle"


def test_transition_is_logged_to_database(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    control = DummyControl()
    service.create_logged_state_machine(
        control, make_transitions(), make_states(), initial="idle"
    )

    control.dummy_trigger("sensor_values")  # type: ignore[attr-defined]

    assert control.state == "running"
    model = added_model(mock_session)
    assert isinstance(model, MachineStateTransition)
    assert model.control_name == "DummyControl"
    assert model.trigger_name == "dummy_trigger"
    assert model.condition_name == "condition_dummy_trigger"
    assert model.state_from == "idle"
    assert model.state_to == "running"
    assert service.last_evaluated_conditions == []


def test_failed_condition_logs_nothing(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    control = DummyControl()
    control.condition_dummy_trigger_result = False
    service.create_logged_state_machine(
        control, make_transitions(), make_states(), initial="idle"
    )

    control.dummy_trigger("sensor_values")  # type: ignore[attr-defined]

    assert control.state == "idle"
    mock_session.add.assert_not_called()


def test_setup_transition_tracking_records_trigger_name(
    service: MachineStateLoggingService,
) -> None:
    control = DummyControl()
    control.dummy_trigger = Mock(return_value=True)  # type: ignore[attr-defined]

    service.setup_transition_tracking(make_transitions(), control)
    control.dummy_trigger("sensor_values")  # type: ignore[attr-defined]

    assert service.last_trigger_name == "dummy_trigger"


def test_setup_condition_tracking_records_passing_conditions(
    service: MachineStateLoggingService,
) -> None:
    control = DummyControl()
    transitions = make_transitions()

    service.setup_condition_tracking(transitions, control)
    wrapped = transitions[0]["conditions"][0]

    assert wrapped("sensor_values") is True
    assert service.last_evaluated_conditions == ["condition_dummy_trigger"]

    control.condition_dummy_trigger_result = False
    assert wrapped("sensor_values") is False
    assert service.last_evaluated_conditions == [
        "condition_dummy_trigger"
    ]  # not added again


def test_before_log_records_current_state(
    service: MachineStateLoggingService,
) -> None:
    control = DummyControl()
    control.state = "idle"

    service._before_log(control, None)

    assert service.last_state == "idle"


def test_after_log_builds_transition_from_tracked_state(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    control = DummyControl()
    control.state = "running"
    service.last_state = "idle"
    service.last_trigger_name = "dummy_trigger"
    service.last_evaluated_conditions = ["condition_dummy_trigger", "pump_ready"]

    service._after_log(control, None)

    model = added_model(mock_session)
    assert isinstance(model, MachineStateTransition)
    assert model.state_from == "idle"
    assert model.state_to == "running"
    assert model.condition_name == "condition_dummy_trigger, pump_ready"
    assert service.last_evaluated_conditions == []


def test_after_log_defaults_to_unknown(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    control = DummyControl()
    control.state = "running"
    service.last_trigger_name = None
    service.last_evaluated_conditions = []

    service._after_log(control, None)

    model = added_model(mock_session)
    assert isinstance(model, MachineStateTransition)
    assert model.trigger_name == "Unknown"
    assert model.condition_name == "Unknown"
