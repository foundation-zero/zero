from unittest import mock

from thrs.classes.control import Control
from thrs.control.switching import AutomationMode
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.orchestration.module import Module


async def test_module_returns_control_when_sensor_values_are_none():
    mock_control = mock.Mock(Control)
    mock_control.initial.return_value = (mock.sentinel.control_values, None)

    mock_alarms = mock.Mock(BaseAlarms)

    mock_channels = mock.AsyncMock()

    module = Module(
        "test",
        mock_control,
        mock_alarms,
        mock_channels,
    )

    control_values = await module.tick(None)

    assert control_values == mock.sentinel.control_values
    assert mock_control.control.call_count == 0
    assert mock_alarms.check.call_count == 0


async def test_module_returns_initial_control_when_manual():
    sensor_values = mock.Mock(
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL))
    )

    mock_control = mock.Mock(Control)
    mock_control.initial.return_value = (mock.sentinel.control_values, None)

    mock_alarms = mock.Mock(BaseAlarms)

    mock_channels = mock.AsyncMock()

    module = Module(
        "test",
        mock_control,
        mock_alarms,
        mock_channels,
    )

    control_values = await module.tick(sensor_values)

    assert control_values == mock.sentinel.control_values
    assert mock_control.control.call_count == 0
    assert mock_alarms.check.call_args_list == [
        mock.call(sensor_values, mock.sentinel.control_values, mock.ANY)
    ]


async def test_module_returns_control_when_automatic():
    sensor_values = mock.Mock(
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL))
    )
    mock_control = mock.Mock(Control)
    mock_control.initial.return_value = (mock.sentinel.initial_control_values, None)
    mock_control.control.return_value = (mock.sentinel.control_values, None)

    mock_alarms = mock.Mock(BaseAlarms)

    mock_channels = mock.AsyncMock()
    mock_channels.get_manual_controls.return_value = None

    module = Module(
        "test",
        mock_control,
        mock_alarms,
        mock_channels,
    )
    module.set_automation_mode(AutomationMode(mode="automatic"))

    control_values = await module.tick(sensor_values)

    assert control_values == mock.sentinel.control_values
    assert mock_control.control.call_args_list == [mock.call(sensor_values)]
    assert mock_alarms.check.call_args_list == [
        mock.call(sensor_values, mock.sentinel.control_values, mock.ANY)
    ]
