import logging
from unittest import mock

from tests.helpers.modules import make_async_channels, make_module
from tests.orchestration.simples import (
    simple_advisory_values,
    simple_control_values,
)
from thrs.control.switching import AutomationMode


async def test_module_returns_control_when_sensor_values_are_none(
    mock_control, mock_alarms, module_factory
):
    mock_control.initial.return_value = (mock.sentinel.control_values, None)

    module = module_factory()

    control_values = await module.tick(None)

    assert control_values == mock.sentinel.control_values
    assert mock_control.control.call_count == 0
    assert mock_alarms.check.call_count == 0


async def test_module_returns_initial_control_when_manual(
    advisory_sensor_values, mock_control, mock_alarms, module_factory
):
    mock_control.initial.return_value = (mock.sentinel.control_values, None)

    module = module_factory()

    control_values = await module.tick(advisory_sensor_values)

    assert control_values == mock.sentinel.control_values
    assert mock_control.control.call_count == 0
    assert mock_alarms.check.call_args_list == [
        mock.call(advisory_sensor_values, mock.sentinel.control_values, mock.ANY)
    ]


async def test_module_returns_control_when_automatic(
    advisory_sensor_values, mock_channels, mock_control, mock_alarms, module_factory
):
    mock_control.initial.return_value = (mock.sentinel.initial_control_values, None)
    mock_control.control.return_value = (mock.sentinel.control_values, None)

    mock_channels.get_manual_controls.return_value = None

    module = module_factory()
    module.set_automation_mode(AutomationMode(mode="automatic"))

    control_values = await module.tick(advisory_sensor_values)

    assert control_values == mock.sentinel.control_values
    assert mock_control.control.call_args_list == [mock.call(advisory_sensor_values)]
    assert mock_alarms.check.call_args_list == [
        mock.call(advisory_sensor_values, mock.sentinel.control_values, mock.ANY)
    ]


async def test_module_forces_manual_and_seeds_actuated_when_not_advisory(
    manual_values, mock_channels, mock_control, module_factory
):
    """Non-advisory means the AMCS is in control: the module must force manual
    mode and seed the manual controls with the actuated control values so a
    later takeover is bumpless."""
    actuated = mock.sentinel.actuated_control_values

    mock_control.initial.return_value = (mock.sentinel.initial_control_values, None)

    mock_channels.get_actuated_control_values.return_value = actuated

    module = module_factory()
    module.set_automation_mode(AutomationMode(mode="automatic"))

    await module.tick(manual_values)

    assert module._control.mode.automatic is False
    assert module._control._manual_control._control_values == actuated


async def test_module_forces_manual_even_without_actuated_values(
    local_sensor_values, mock_channels, mock_control, module_factory
):
    """Without actuated feedback we can still not stay automatic when the
    AMCS is in control; manual controls keep their last value."""
    initial_control_values = {"dutypoint": 0.5}
    mock_control.initial.return_value = (initial_control_values, None)
    mock_control.control.return_value = (initial_control_values, None)

    mock_channels.get_actuated_control_values.return_value = None
    mock_channels.get_manual_controls.return_value = None

    module = module_factory()
    module.set_automation_mode(AutomationMode(mode="automatic"))

    await module.tick(local_sensor_values)

    assert module._control.mode.automatic is False
    assert mock_channels.get_actuated_control_values.call_count == 1
    # The manual controls keep the initial value: without actuated feedback
    # there is nothing to seed them with.
    assert mock_channels.send_manual_control.await_args == mock.call(
        initial_control_values
    )


async def test_tick_publishes_actuated_echo_when_not_advisory(
    manual_values, mock_channels, mock_control, module_factory
):
    """While the AMCS is not in advisory mode the module must still publishes,
    echoing the actuated values."""
    actuated = simple_control_values(flow=6.0)

    mock_control.initial.return_value = (simple_control_values(flow=1.0), None)

    mock_channels.get_actuated_control_values.return_value = actuated

    module = module_factory()

    control_values = await module.tick(manual_values)

    assert control_values == actuated
    assert mock_channels.send_control_values.await_args == mock.call(actuated)
    assert mock_channels.send_manual_control.await_args == mock.call(actuated)


async def test_automatic_control_sends_manual_as_first_value(
    advisory_sensor_values, manual_values, mock_channels, mock_control, module_factory
):
    initial = simple_control_values(flow=1.0)
    actuated = simple_control_values(flow=6.0)
    mock_control.initial.return_value = (initial, None)
    mock_control.control.return_value = (actuated, None)
    mock_channels.get_actuated_control_values.return_value = actuated

    module = module_factory()

    manual_control_values = await module.tick(manual_values)
    module.set_automation_mode(AutomationMode(mode="automatic"))
    automatic_control_values = await module.tick(advisory_sensor_values)

    assert manual_control_values == actuated
    mock_control.update_controls.assert_called_once_with(actuated)
    assert automatic_control_values == actuated
    assert automatic_control_values != initial


async def test_disable_warning_names_module(
    caplog, manual_values, mock_channels, mock_control, module_factory
):
    """When the advisory mode for a model is disabled, a warning is triggered"""
    mock_control.initial.return_value = (simple_control_values(flow=1.0), None)

    mock_channels.get_actuated_control_values.return_value = simple_control_values(
        flow=6.0
    )

    module = module_factory(name="dummy")

    await module.tick(simple_advisory_values(flow=1.0))
    with caplog.at_level(logging.WARNING, logger="thrs.control.switching"):
        await module.tick(manual_values)

    assert any(
        "advisory was disabled for dummy" in record.message for record in caplog.records
    )


async def test_tick_without_sensors_echoes_actuated(manual_values):
    """A sensor gap publishes the last actuated values"""
    channels = make_async_channels()
    actuated = simple_control_values(flow=6.0)
    channels.get_actuated_control_values.return_value = actuated

    module = make_module(channels=channels)

    control_values = await module.tick(manual_values)
    assert control_values == actuated

    control_values = await module.tick(None)
    assert control_values == actuated
