from unittest.mock import Mock

import pytest

from tests.classes.machine_state_logger.conftest import DummyThrsValues
from thrs.classes.machine_state_logger import (
    MachineStateLoggingService,
    StateLogger,
)
from thrs.input_output.alarms import Alarm, Severity

OVERHEATING = Alarm(
    code="Overheating alarm",
    message="supply temperature above 95 °C",
    severity=Severity.ALARM,
)
TANK_WARNING = Alarm(
    code="Tank 1 high temperature warning",
    message="tank 1 at 63.0°C, above maximum 60°C",
    severity=Severity.WARNING,
)


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


class DecoratedModule:
    """Mirrors Module, which exposes the control's logger as control_state_logger."""

    def __init__(self, control_state_logger: Mock | None) -> None:
        self.control_state_logger = control_state_logger

    @StateLogger.log_alarms
    def check_alarms(self) -> list[Alarm]:
        return [OVERHEATING, TANK_WARNING]


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


def test_log_alarms_decorator_logs_each_alarm_and_returns_result() -> None:
    state_logger = Mock(spec=MachineStateLoggingService)
    module = DecoratedModule(state_logger)

    result = module.check_alarms()

    assert result == [OVERHEATING, TANK_WARNING]
    assert [call.args[0] for call in state_logger.log_alarm.call_args_list] == [
        OVERHEATING,
        TANK_WARNING,
    ]


def test_log_alarms_decorator_preserves_per_alarm_severity() -> None:
    state_logger = Mock(spec=MachineStateLoggingService)
    module = DecoratedModule(state_logger)

    module.check_alarms()

    severities = [
        call.args[0].severity for call in state_logger.log_alarm.call_args_list
    ]
    assert severities == [Severity.ALARM, Severity.WARNING]


def test_log_alarms_decorator_without_logger_still_runs() -> None:
    module = DecoratedModule(control_state_logger=None)

    assert module.check_alarms() == [OVERHEATING, TANK_WARNING]
