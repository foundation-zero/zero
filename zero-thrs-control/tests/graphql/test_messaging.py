from unittest import mock

from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.graphql.messaging import (
    ControlMessaging,
    DirectiveMessaging,
    SimulationMessaging,
)
from thrs.input_output.base import ThrsValues


class DummyValues(ThrsValues):
    test: bool = False


async def test_control_messaging_set_manual_control():
    mock_channels = mock.AsyncMock()
    mock_channels.get_manual_values = mock.Mock(return_value=DummyValues())

    messaging = ControlMessaging(mock_channels)
    messaging.active = True

    result = await messaging.set_manual_control("test", True)

    assert result == DummyValues(test=True)
    assert mock_channels.get_manual_values.call_count == 1
    assert mock_channels.wait_for_manual_values.call_count == 1

    # Waits for the correct condition
    assert mock_channels.wait_for_manual_values.call_args[0][0](DummyValues(test=True))
    assert not mock_channels.wait_for_manual_values.call_args[0][0](
        DummyValues(test=False)
    )

    assert mock_channels.send_manual_values.call_args_list == [
        mock.call(DummyValues(test=True))
    ]


async def test_control_messaging_set_parameter():
    mock_channels = mock.AsyncMock()
    mock_channels.get_parameters = mock.Mock(return_value=DummyValues())

    messaging = ControlMessaging(mock_channels)
    messaging.active = True

    result = await messaging.set_parameter("test", True)

    assert result == DummyValues(test=True)
    assert mock_channels.get_parameters.call_count == 1
    assert mock_channels.wait_for_parameters.call_count == 1

    # Waits for the correct condition
    assert mock_channels.wait_for_parameters.call_args[0][0](DummyValues(test=True))
    assert not mock_channels.wait_for_parameters.call_args[0][0](
        DummyValues(test=False)
    )

    assert mock_channels.send_parameters.call_args_list == [
        mock.call(DummyValues(test=True))
    ]


async def test_control_messaging_set_automation_mode():
    mock_channels = mock.AsyncMock()

    messaging = ControlMessaging(mock_channels)
    messaging.active = True

    result = await messaging.set_automation_mode(True)

    assert result is True
    assert mock_channels.wait_for_control_modes.call_count == 1

    # Waits for the correct condition
    assert mock_channels.wait_for_control_modes.call_args[0][0](
        SwitchingControlMode(automatic_mode=DummyValues(test=True))
    )
    assert not mock_channels.wait_for_control_modes.call_args[0][0](
        SwitchingControlMode(automatic_mode=None)
    )

    assert mock_channels.send_automation_mode.call_args_list == [
        mock.call(AutomationMode(mode="automatic"))
    ]


async def test_directive_messaging_pause_simulation():
    mock_channels = mock.AsyncMock()
    mock_channels.on_simulation_status.return_value = None
    mock_channels.get_simulation_status = mock.Mock(
        return_value=mock.Mock(status="running")
    )

    messaging = DirectiveMessaging([], mock_channels)

    await messaging.pause_simulation()

    assert mock_channels.get_simulation_status.call_count == 1
    assert mock_channels.wait_for_simulation_status_where.call_count == 1

    # Waits for the correct condition
    assert mock_channels.wait_for_simulation_status_where.call_args[0][0](
        mock.Mock(status="available")
    )
    assert not mock_channels.wait_for_simulation_status_where.call_args[0][0](
        mock.Mock(status="stepping")
    )

    assert mock_channels.send_pause.call_args_list == [mock.call()]


async def test_directive_messaging_play_simulation():
    mock_channels = mock.AsyncMock()
    mock_channels.on_simulation_status.return_value = None
    mock_channels.get_simulation_status = mock.Mock(
        return_value=mock.Mock(status="available")
    )

    messaging = DirectiveMessaging([], mock_channels)

    await messaging.play_simulation(1)

    assert mock_channels.get_simulation_status.call_count == 1
    assert mock_channels.wait_for_simulation_status_where.call_count == 1

    # Waits for the correct condition
    assert mock_channels.wait_for_simulation_status_where.call_args[0][0](
        mock.Mock(status="running")
    )
    assert not mock_channels.wait_for_simulation_status_where.call_args[0][0](
        mock.Mock(status="stepping")
    )

    assert mock_channels.send_play.call_args_list == [mock.call(1)]


async def test_directive_messaging_step_simulation():
    mock_channels = mock.AsyncMock()
    mock_channels.on_simulation_status.return_value = None
    mock_channels.get_simulation_status = mock.Mock(
        return_value=mock.Mock(status="available")
    )

    messaging = DirectiveMessaging([], mock_channels)

    await messaging.step_simulation(1)

    assert mock_channels.get_simulation_status.call_count == 1
    assert mock_channels.wait_for_simulation_status_where.call_count == 1

    # Waits for the correct condition
    assert mock_channels.wait_for_simulation_status_where.call_args[0][0](
        mock.Mock(status="stepping")
    )
    assert not mock_channels.wait_for_simulation_status_where.call_args[0][0](
        mock.Mock(status="running")
    )

    assert mock_channels.send_step.call_args_list == [mock.call(1)]


async def test_control_messaging_set_simulation_input():
    mock_channels = mock.AsyncMock()
    mock_channels.get_simulation_inputs = mock.Mock(return_value=DummyValues())

    messaging = SimulationMessaging(mock_channels)

    result = await messaging.set_simulation_input("test", True)

    assert result == DummyValues(test=True)
    assert mock_channels.get_simulation_inputs.call_count == 1
    assert mock_channels.wait_for_simulation_inputs.call_count == 1

    # Waits for the correct condition
    assert mock_channels.wait_for_simulation_inputs.call_args[0][0](
        DummyValues(test=True)
    )
    assert not mock_channels.wait_for_simulation_inputs.call_args[0][0](
        DummyValues(test=False)
    )

    assert mock_channels.send_simulation_inputs.call_args_list == [
        mock.call(DummyValues(test=True))
    ]
