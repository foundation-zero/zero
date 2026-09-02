import asyncio
from unittest.mock import Mock

from tests.classes.machine_state_logger.conftest import added_model
from thrs.classes.machine_state_logger import MachineStateLogger
from thrs.db.models.machine_state import (
    MachineStateEvent,
    MachineStateIssue,
    MachineStateParametersUpdate,
    MachineStateTransition,
)
from thrs.input_output.alarms import Severity


def test_log_event_saves_to_database(
    logger: MachineStateLogger, mock_session: Mock
) -> None:
    event = MachineStateEvent(
        control_name="TestControl", event_name="started", event_details="details"
    )

    logger.log_event(event)

    model = added_model(mock_session)
    assert model is event


def test_log_transition_saves_to_database(
    logger: MachineStateLogger, mock_session: Mock
) -> None:
    transition = MachineStateTransition(
        control_name="TestControl",
        trigger_name="go",
        condition_name="can_go",
        state_from="idle",
        state_to="running",
    )

    logger.log_transition(transition)

    assert added_model(mock_session) is transition


def test_log_parameters_saves_to_database(
    logger: MachineStateLogger, mock_session: Mock
) -> None:
    parameters = MachineStateParametersUpdate(
        control_name="TestControl",
        data_container_name="DummyParameters",
        parameters_from=None,
        parameters_to={},
        parameters_diff=None,
    )

    logger.log_parameters(parameters)

    assert added_model(mock_session) is parameters


def test_log_alarm_saves_issue_with_severity(
    logger: MachineStateLogger, mock_session: Mock
) -> None:
    logger.log_alarm("PumpAlarm", Severity.ALARM, "pump failure")

    model = added_model(mock_session)
    assert isinstance(model, MachineStateIssue)
    assert model.control_name == "PumpAlarm"
    assert model.severity_level == Severity.ALARM
    assert model.issue_details == "pump failure"
    assert model.timestamp.tzinfo is not None


def test_log_warning_saves_issue_with_warning_severity(
    logger: MachineStateLogger, mock_session: Mock
) -> None:
    logger.log_warning("something looks off")

    model = added_model(mock_session)
    assert isinstance(model, MachineStateIssue)
    assert model.control_name == "Warning"
    assert model.severity_level == Severity.WARNING
    assert model.issue_details == "something looks off"


async def test_log_model_in_running_loop_saves_to_database(
    logger: MachineStateLogger, mock_session: Mock
) -> None:
    # Inside a running event loop the write is scheduled as a task.
    logger.log_issue(
        MachineStateIssue(
            control_name="TestControl",
            severity_level=Severity.WARNING,
            issue_details=None,
        )
    )
    await asyncio.sleep(0)  # give the scheduled task a chance to run

    mock_session.add.assert_called_once()
