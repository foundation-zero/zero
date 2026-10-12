import asyncio
from contextlib import asynccontextmanager
from unittest.mock import Mock, patch

import pytest

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


def _flaky_postgres_db(mock_session: Mock, failures: int) -> Mock:
    remaining = [failures]

    @asynccontextmanager
    async def begin():
        if remaining[0] > 0:
            remaining[0] -= 1
            raise ConnectionRefusedError(111, "Connect call failed")
        yield mock_session

    postgres_db = Mock()
    postgres_db.session_factory.begin = begin
    return postgres_db


@pytest.fixture
def no_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    async def sleep(delay_s: float) -> None:
        await asyncio.sleep(0)

    monkeypatch.setattr("thrs.classes.database.sleep", sleep)


@pytest.mark.usefixtures("no_backoff")
async def test_log_retries_through_a_switchover(mock_session: Mock) -> None:
    logger = MachineStateLogger(_flaky_postgres_db(mock_session, failures=3))
    loop = asyncio.get_running_loop()

    logger.log_warning("during switchover")
    await logger.wait_for_pending_tasks()

    assert loop.is_running()
    mock_session.add.assert_called_once()


@pytest.mark.usefixtures("no_backoff")
async def test_log_keeps_order_while_retrying(mock_session: Mock) -> None:
    logger = MachineStateLogger(_flaky_postgres_db(mock_session, failures=2))

    logger.log_warning("first")
    logger.log_warning("second")
    await logger.wait_for_pending_tasks()

    details = [call.args[0].issue_details for call in mock_session.add.call_args_list]
    assert details == ["first", "second"]


@pytest.mark.usefixtures("no_backoff")
async def test_log_stops_loop_when_retry_budget_runs_out(mock_session: Mock) -> None:
    logger = MachineStateLogger(
        _flaky_postgres_db(mock_session, failures=1), retry_budget_s=0
    )

    with _stop_spy() as stop:
        logger.log_warning("database gone")
        await logger.wait_for_pending_tasks()
        await asyncio.sleep(0)

    stop.assert_called_once()
    mock_session.add.assert_not_called()


async def test_log_stops_loop_on_non_transient_error(
    postgres_db: Mock, mock_session: Mock
) -> None:
    mock_session.add.side_effect = ValueError("not a connection problem")
    logger = MachineStateLogger(postgres_db)

    with _stop_spy() as stop:
        logger.log_warning("bad row")
        await logger.wait_for_pending_tasks()
        await asyncio.sleep(0)

    stop.assert_called_once()
    mock_session.add.assert_called_once()


def _stop_spy():
    """pytest-asyncio ends each test with `loop.stop()`, so the spy must not outlive the block."""
    return patch.object(asyncio.get_running_loop(), "stop")
