import warnings
from unittest.mock import Mock

import pytest

from tests.classes.machine_state_logger.conftest import DummyThrsValues
from thrs.classes.machine_state_logger import (
    MachineStateLoggingService,
    StateLogger,
)
from thrs.input_output.alarms import Severity


class DecoratedControl:
    def __init__(self, state_logger: Mock | None) -> None:
        self.state_logger = state_logger
        self._parameters = DummyThrsValues(flow=1.0)

    @StateLogger.log_parameters
    def update_parameters(self, parameters: DummyThrsValues) -> None:
        self.updated = parameters

    @StateLogger.log_warnings
    def warn(self) -> None:
        raise Warning("watch out")

    @StateLogger.log_alarms
    def alarm(self) -> str:
        warnings.warn("overheating")
        return "done"


def test_log_parameters_decorator_logs_change_and_updates() -> None:
    state_logger = Mock(spec=MachineStateLoggingService)
    control = DecoratedControl(state_logger)
    new_parameters = DummyThrsValues(flow=2.0)

    control.update_parameters(new_parameters)

    state_logger.log_parameters_on_change.assert_called_once()
    kwargs = state_logger.log_parameters_on_change.call_args.kwargs
    assert kwargs["values_from"].flow == 1.0
    assert kwargs["values_to"].flow == 2.0
    assert control._parameters is new_parameters
    assert control.updated is new_parameters


def test_log_parameters_decorator_without_logger() -> None:
    control = DecoratedControl(state_logger=None)
    new_parameters = DummyThrsValues(flow=2.0)

    control.update_parameters(new_parameters)

    assert control._parameters is new_parameters


def test_log_warnings_decorator_logs_and_reraises() -> None:
    state_logger = Mock(spec=MachineStateLoggingService)
    control = DecoratedControl(state_logger)

    with pytest.raises(Warning, match="watch out"):
        control.warn()

    state_logger.log_warning.assert_called_once_with("watch out")


def test_log_alarms_decorator_logs_alarm_and_returns_result() -> None:
    state_logger = Mock(spec=MachineStateLoggingService)
    control = DecoratedControl(state_logger)

    result = control.alarm()

    assert result == "done"
    state_logger.log_issue.assert_called_once_with(
        message="overheating", severity=Severity.ALARM
    )


def test_log_alarms_decorator_without_logger_still_runs() -> None:
    control = DecoratedControl(state_logger=None)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert control.alarm() == "done"
