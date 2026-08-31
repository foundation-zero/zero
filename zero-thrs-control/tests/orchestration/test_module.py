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


async def test_module_forces_manual_and_seeds_actuated_when_not_advisory():
    """Non-advisory means the AMCS is in control: the module must force manual
    mode and seed the manual controls with the actuated control values so a
    later takeover is bumpless."""
    sensor_values = mock.Mock(
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.MANUAL))
    )
    actuated = mock.sentinel.actuated_control_values

    mock_control = mock.Mock()
    mock_control.initial.return_value = (mock.sentinel.initial_control_values, None)

    mock_alarms = mock.Mock()
    mock_alarms.check.return_value = []

    mock_channels = mock.Mock()
    mock_channels.get_actuated_control_values.return_value = actuated
    mock_channels.send_control_values = mock.AsyncMock()
    mock_channels.send_computed_values = mock.AsyncMock()
    mock_channels.send_controller_state = mock.AsyncMock()
    mock_channels.send_parameters = mock.AsyncMock()
    mock_channels.send_control_modes = mock.AsyncMock()
    mock_channels.send_manual_control = mock.AsyncMock()

    module = Module(
        "test",
        mock_control,
        mock_alarms,
        mock_channels,
    )
    module.set_automation_mode(AutomationMode(mode="automatic"))

    await module.tick(sensor_values)

    assert module._control.mode.automatic is False
    assert module._control._manual_control._control_values == actuated


async def test_module_forces_manual_even_without_actuated_values():
    """Without actuated feedback we can still not stay automatic when the
    AMCS is in control; manual controls keep their last value."""
    sensor_values = mock.Mock(
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.LOCAL))
    )

    initial_control_values = {"dutypoint": 0.5}
    mock_control = mock.Mock()
    mock_control.initial.return_value = (initial_control_values, None)
    mock_control.control.return_value = (initial_control_values, None)

    mock_alarms = mock.Mock()
    mock_alarms.check.return_value = []

    mock_channels = mock.Mock()
    mock_channels.get_actuated_control_values.return_value = None
    mock_channels.get_manual_controls.return_value = None
    mock_channels.send_control_values = mock.AsyncMock()
    mock_channels.send_computed_values = mock.AsyncMock()
    mock_channels.send_controller_state = mock.AsyncMock()
    mock_channels.send_parameters = mock.AsyncMock()
    mock_channels.send_control_modes = mock.AsyncMock()
    mock_channels.send_manual_control = mock.AsyncMock()

    module = Module(
        "test",
        mock_control,
        mock_alarms,
        mock_channels,
    )
    module.set_automation_mode(AutomationMode(mode="automatic"))

    await module.tick(sensor_values)

    assert module._control.mode.automatic is False
    assert mock_channels.get_actuated_control_values.call_count == 1
    # The manual controls keep the initial value: without actuated feedback
    # there is nothing to seed them with.
    assert mock_channels.send_manual_control.await_args == mock.call(
        initial_control_values
    )
