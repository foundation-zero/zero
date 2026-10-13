from unittest.mock import Mock

from tests.classes.machine_state_logger.conftest import added_model
from thrs.classes.machine_state_logger import MachineStateLoggingService
from thrs.db.models.machine_state import MachineStateEvent, MachineStateIssue
from thrs.input_output.alarms import Severity


def test_service_log_issue(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    service.log_issue("too hot", Severity.ALARM)

    model = added_model(mock_session)
    assert isinstance(model, MachineStateIssue)
    assert model.control_name == "MachineStateLoggingService"
    assert model.severity_level == Severity.ALARM
    assert model.issue_details == "too hot"


def test_service_log_warning(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    service.log_warning("careful")

    model = added_model(mock_session)
    assert isinstance(model, MachineStateIssue)
    assert model.severity_level == Severity.WARNING


def test_service_log_event(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    event = MachineStateEvent(
        control_name="TestControl", event_name="tick", event_details=None
    )

    service.log_event(event)

    assert added_model(mock_session) is event
