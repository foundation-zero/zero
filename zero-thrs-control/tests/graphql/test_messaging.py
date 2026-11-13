from datetime import UTC, datetime, timedelta
from unittest import mock

import pytest

from thrs.control.switching import AutomationMode
from thrs.graphql.messaging import (
    ControlMessaging,
    DirectiveMessaging,
    SimulationMessaging,
)
from thrs.input_output.base import ThrsValues
from thrs.runtime.messages import (
    SimulationStatus,
    SimulationStatusMessage,
    SimulationStatusSetMessage,
)

START = datetime(2026, 11, 13, 10, tzinfo=UTC)


class DummyValues(ThrsValues):
    test: bool = False


async def test_control_messaging_set_manual_control():
    mock_channels = mock.AsyncMock()
    mock_channels.get_actuated_control_values = mock.Mock(return_value=DummyValues())

    messaging = ControlMessaging(mock_channels)

    result = await messaging.set_manual_control("test", True)

    assert result == DummyValues(test=True)
    assert mock_channels.get_actuated_control_values.call_count == 1
    assert mock_channels.wait_for_actuated_control_values.call_count == 1

    # Waits for the correct condition
    assert mock_channels.wait_for_actuated_control_values.call_args[0][0](
        DummyValues(test=True)
    )
    assert not mock_channels.wait_for_actuated_control_values.call_args[0][0](
        DummyValues(test=False)
    )

    assert mock_channels.send_manual_values.call_args_list == [
        mock.call(DummyValues(test=True))
    ]


async def test_control_messaging_set_parameter():
    mock_channels = mock.AsyncMock()
    mock_channels.get_parameters = mock.Mock(return_value=DummyValues())

    messaging = ControlMessaging(mock_channels)

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


async def test_control_messaging_control_values_is_actuated():
    mock_channels = mock.Mock()
    messaging = ControlMessaging(mock_channels)

    mock_channels.get_actuated_control_values.return_value = None
    assert messaging.control_values is None
    mock_channels.get_actuated_control_values.assert_called_once()

    mock_channels.get_actuated_control_values.return_value = DummyValues(test=True)
    assert messaging.control_values == DummyValues(test=True)


async def test_control_messaging_set_automation_mode():
    mock_channels = mock.AsyncMock()

    messaging = ControlMessaging(mock_channels)

    result = await messaging.set_automation_mode(True)

    assert result is True
    assert mock_channels.wait_for_automation_mode.call_count == 1

    # Waits until the module publishes that it took the mode
    condition = mock_channels.wait_for_automation_mode.call_args[0][0]
    assert condition(AutomationMode(mode="automatic"))
    assert not condition(AutomationMode(mode="manual"))

    assert mock_channels.send_automation_mode.call_args_list == [
        mock.call(AutomationMode(mode="automatic"))
    ]


def simulation_status(
    status: SimulationStatus,
    playback_rate: float = 1.0,
    pause_at: datetime | None = None,
) -> SimulationStatusMessage:
    return SimulationStatusMessage(
        mode="thrs",
        status=status,
        control_modules=[],
        simulation_time=START,
        playback_rate=playback_rate,
        pause_at=pause_at,
    )


async def test_directive_messaging_pause_simulation():
    mock_channels = mock.AsyncMock()
    mock_channels.on_simulation_status = mock.Mock()
    mock_channels.get_simulation_status = mock.Mock(
        return_value=simulation_status("running", playback_rate=2.0)
    )

    messaging = DirectiveMessaging([], mock_channels)

    await messaging.pause_simulation()

    assert mock_channels.get_simulation_status.call_count == 1
    assert mock_channels.wait_for_simulation_status_where.call_count == 1

    # Waits for the correct condition
    condition = mock_channels.wait_for_simulation_status_where.call_args[0][0]
    assert condition(simulation_status("available", playback_rate=2.0))
    assert not condition(simulation_status("stepping", playback_rate=2.0))

    assert mock_channels.send_status_set.call_args_list == [
        mock.call(
            SimulationStatusSetMessage(
                status="available", playback_rate=2.0, pause_at=None
            )
        )
    ]


async def test_directive_messaging_play_simulation():
    mock_channels = mock.AsyncMock()
    mock_channels.on_simulation_status = mock.Mock()
    mock_channels.get_simulation_status = mock.Mock(
        return_value=simulation_status("available")
    )

    messaging = DirectiveMessaging([], mock_channels)

    await messaging.play_simulation(1)

    assert mock_channels.get_simulation_status.call_count == 1
    assert mock_channels.wait_for_simulation_status_where.call_count == 1

    # Waits for the correct condition: running already, at another rate or until a
    # PauseAt, is not yet what was asked for.
    condition = mock_channels.wait_for_simulation_status_where.call_args[0][0]
    assert condition(simulation_status("running", playback_rate=1))
    assert not condition(simulation_status("running", playback_rate=2.0))
    assert not condition(
        simulation_status("running", pause_at=START + timedelta(hours=1))
    )
    assert not condition(simulation_status("stepping"))

    assert mock_channels.send_status_set.call_args_list == [
        mock.call(
            SimulationStatusSetMessage(status="running", playback_rate=1, pause_at=None)
        )
    ]


async def test_directive_messaging_step_simulation():
    mock_channels = mock.AsyncMock()
    mock_channels.on_simulation_status = mock.Mock()
    mock_channels.get_simulation_status = mock.Mock(
        return_value=simulation_status("available")
    )

    messaging = DirectiveMessaging([], mock_channels)

    await messaging.step_simulation(1)

    assert mock_channels.get_simulation_status.call_count == 1
    assert mock_channels.wait_for_simulation_status_where.call_count == 1

    # Waits for the correct condition
    condition = mock_channels.wait_for_simulation_status_where.call_args[0][0]
    assert condition(
        simulation_status("stepping", pause_at=START + timedelta(seconds=1))
    )
    assert not condition(simulation_status("stepping"))
    assert not condition(
        simulation_status("running", pause_at=START + timedelta(seconds=1))
    )

    assert mock_channels.send_status_set.call_args_list == [
        mock.call(
            SimulationStatusSetMessage(
                status="stepping",
                playback_rate=1.0,
                pause_at=START + timedelta(seconds=1),
            )
        )
    ]


@pytest.mark.parametrize("seconds", [0, -1])
async def test_directive_messaging_step_rejects_no_positive_seconds(seconds: float):
    mock_channels = mock.AsyncMock()
    mock_channels.on_simulation_status = mock.Mock()
    mock_channels.get_simulation_status = mock.Mock(
        return_value=simulation_status("available")
    )

    messaging = DirectiveMessaging([], mock_channels)

    with pytest.raises(Exception, match="positive number of seconds"):
        await messaging.step_simulation(seconds)

    mock_channels.send_status_set.assert_not_called()


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
