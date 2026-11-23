import pytest
from pydantic import ValidationError

from tests.helpers.modules import (
    ConfigurableParameters,
    make_async_channels,
    make_module,
    simple_control_values,
)
from thrs.classes.persistence.engine import InMemoryPersistentEngine
from thrs.classes.persistence.manager import PersistManager
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.control.state import AutomationMode

DEFAULTS = ConfigurableParameters()


async def test_controller_state_starts_in_manual_with_defaults():
    _, state = await make_module().tick(None)

    assert state.automation_mode == AutomationMode(mode="manual")
    assert state.parameters == DEFAULTS


async def test_controller_state_follows_automation_mode():
    module = make_module()
    module.set_automation_mode(AutomationMode(mode="automatic"))

    _, state = await module.tick(None)
    assert state.automation_mode == AutomationMode(mode="automatic")


async def test_applied_snapshot_reproduces_the_channel_updates():
    channels = make_async_channels()
    channels.get_parameters.return_value = ConfigurableParameters(setpoint=72.5)
    channels.get_manual_controls.return_value = simple_control_values(3.5)
    channels.get_automation_modes.return_value = AutomationMode(mode="automatic")

    source = make_module(channels=channels)
    await source.sync_control_channels_state()
    _, source_state = await source.tick(None)

    restored = make_module()
    restored.apply_persistence_snapshot(
        ModulePersistenceSnapshot.from_controller_state(source_state)
    )
    _, restored_state = await restored.tick(None)

    assert restored_state.parameters == ConfigurableParameters(setpoint=72.5)
    assert restored_state.automation_mode == AutomationMode(mode="automatic")


def test_apply_snapshot_rejects_parameters_that_no_longer_validate():
    module = make_module()

    with pytest.raises(ValidationError):
        module.apply_persistence_snapshot(
            ModulePersistenceSnapshot(parameters={"setpoint": "warm"})
        )


async def test_apply_snapshot_rejects_out_of_bound_parameters():
    module = make_module()

    with pytest.raises(ValidationError):
        module.apply_persistence_snapshot(
            ModulePersistenceSnapshot(parameters={"setpoint": 1_000_000.0})
        )

    _, state = await module.tick(None)
    assert state.parameters == DEFAULTS


async def test_apply_snapshot_is_atomic_when_control_mode_is_invalid():
    """A snapshot with valid parameters but a corrupt control mode (e.g. bypassing
    normal validation, as a hand-edited DB row would) must not partially apply -
    the parameters must not change if the mode switch fails."""
    module = make_module()
    corrupt = ModulePersistenceSnapshot.model_construct(
        parameters={"setpoint": 60.0},
        control_mode="deleted-enum-value",  # pyrefly: ignore[bad-argument-type]
    )

    with pytest.raises(ValidationError):
        module.apply_persistence_snapshot(corrupt)

    _, state = await module.tick(None)
    assert state.parameters == DEFAULTS
    assert state.automation_mode == AutomationMode(mode="manual")


async def test_apply_snapshot_with_unchanged_default_values_applies_correctly():
    """Applying a module's own (unmodified) default snapshot back to itself should
    be a no-op: same parameters, same mode."""
    module = make_module()
    _, default_state = await module.tick(None)

    module.apply_persistence_snapshot(
        ModulePersistenceSnapshot.from_controller_state(default_state)
    )

    _, state = await module.tick(None)
    assert state.parameters == default_state.parameters
    assert state.automation_mode == default_state.automation_mode


async def test_persist_then_restore_reproduces_the_controller_state():
    channels = make_async_channels()
    channels.get_parameters.return_value = ConfigurableParameters(setpoint=65.0)
    channels.get_automation_modes.return_value = AutomationMode(mode="automatic")

    store = InMemoryPersistentEngine()
    running = make_module(channels=channels)
    await running.sync_control_channels_state()
    _, running_state = await running.tick(None)
    await PersistManager(store).persist(running.name, running_state)

    restarted = make_module()
    restored = await PersistManager(store).restore(restarted)

    assert restored is True
    _, restarted_state = await restarted.tick(None)
    assert restarted_state.parameters == running_state.parameters
    assert restarted_state.automation_mode == running_state.automation_mode
