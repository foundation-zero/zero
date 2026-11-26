from datetime import datetime
from unittest import mock

import pytest
from pydantic import ValidationError

from tests.helpers.modules import (
    CONFIGURABLE_MODULE_DESCRIPTION,
    ConfigurableParameters,
    make_async_channels,
    make_module,
)
from thrs.cli.setup import setup_control_modules
from thrs.control.state import AutomationMode
from thrs.orchestration.comms import MqttConnector
from thrs.orchestration.config import Config
from thrs.persistence.engine import InMemoryPersistentEngine
from thrs.persistence.manager import PersistManager

DEFAULTS = ConfigurableParameters()


async def test_a_module_starts_in_manual_with_defaults():
    _, state = await make_module().tick(None)

    assert state.automation_mode == AutomationMode(mode="manual")
    assert state.parameters == DEFAULTS


async def test_a_module_starts_with_the_given_parameters_and_mode():
    module = make_module(
        parameters=ConfigurableParameters(setpoint=60.0), automation_mode="automatic"
    )

    _, state = await module.tick(None)
    assert state.parameters == ConfigurableParameters(setpoint=60.0)
    assert state.automation_mode == AutomationMode(mode="automatic")


def test_a_module_rejects_an_unknown_mode():
    with pytest.raises(ValidationError):
        make_module(automation_mode="deleted-enum-value")  # pyrefly: ignore[bad-argument-type]


async def test_controller_state_follows_automation_mode():
    module = make_module()
    module.set_automation_mode(AutomationMode(mode="automatic"))

    _, state = await module.tick(None)
    assert state.automation_mode == AutomationMode(mode="automatic")


async def test_a_restarted_module_continues_from_the_persisted_controller_state(
    settings: Config,
):
    channels = make_async_channels()
    channels.get_parameters.return_value = ConfigurableParameters(setpoint=65.0)
    channels.get_automation_modes.return_value = AutomationMode(mode="automatic")

    store = InMemoryPersistentEngine()
    running = make_module(channels=channels)
    await running.sync_control_channels_state()
    _, running_state = await running.tick(None)
    await PersistManager(store).persist(running.name, running_state)

    [restarted] = await setup_control_modules(
        MqttConnector(mock.AsyncMock()),
        settings,
        {"test": CONFIGURABLE_MODULE_DESCRIPTION},
        datetime.now,
        PersistManager(store),
    )

    _, restarted_state = await restarted.tick(None)
    assert restarted_state.parameters == running_state.parameters
    assert restarted_state.automation_mode == running_state.automation_mode
