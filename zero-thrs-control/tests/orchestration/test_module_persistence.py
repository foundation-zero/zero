import logging

import pytest
from pydantic import ValidationError

from tests.helpers.modules import (
    ConfigurableParameters,
    make_channels,
    make_module,
    manual_values,
)
from thrs.classes.persistence.engine import InMemoryPersistentEngine
from thrs.classes.persistence.manager import PersistManager
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.control.switching import AutomationMode


def test_persistence_snapshot_starts_in_manual_with_defaults():
    snapshot = make_module().get_persistence_snapshot()

    assert snapshot.control_mode == "manual"
    assert snapshot.parameters == {"setpoint": 50.0}
    assert snapshot.manual_control_values is not None


def test_persistence_snapshot_follows_automation_mode():
    module = make_module()
    module.set_automation_mode(AutomationMode(mode="automatic"))

    assert module.get_persistence_snapshot().control_mode == "automatic"


async def test_persistence_snapshot_round_trips_channel_updates():
    channels = make_channels()
    channels.get_parameters.return_value = ConfigurableParameters(setpoint=72.5)
    channels.get_manual_controls.return_value = manual_values(3.5)
    channels.get_automation_modes.return_value = AutomationMode(mode="automatic")

    source = make_module(channels=channels)
    await source.sync_control_channels_state()
    snapshot = source.get_persistence_snapshot()

    restored = make_module()
    restored.apply_persistence_snapshot(snapshot)

    assert restored.get_persistence_snapshot() == snapshot
    assert snapshot.parameters == {"setpoint": 72.5}
    assert snapshot.control_mode == "automatic"


def test_apply_snapshot_rejects_parameters_that_no_longer_validate():
    module = make_module()

    with pytest.raises(ValidationError):
        module.apply_persistence_snapshot(
            ModulePersistenceSnapshot(parameters={"setpoint": "warm"})
        )


def test_apply_snapshot_rejects_out_of_bound_parameters():
    module = make_module()

    with pytest.raises(ValidationError):
        module.apply_persistence_snapshot(
            ModulePersistenceSnapshot(parameters={"setpoint": 1_000_000.0})
        )

    assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}


def test_apply_snapshot_is_atomic_when_control_mode_is_invalid():
    """A snapshot with valid parameters but a corrupt control mode (e.g. bypassing
    normal validation, as a hand-edited DB row would) must not partially apply -
    the parameters must not change if the mode switch fails."""
    module = make_module()
    corrupt = ModulePersistenceSnapshot.model_construct(
        parameters={"setpoint": 60.0},
        manual_control_values=None,
        control_mode="deleted-enum-value",  # type: ignore[arg-type]
    )

    with pytest.raises(ValidationError):
        module.apply_persistence_snapshot(corrupt)

    assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}
    assert module.get_persistence_snapshot().control_mode == "manual"


def test_apply_snapshot_with_unchanged_default_values_applies_correctly():
    """Applying a module's own (unmodified) default snapshot back to itself should
    be a no-op: same parameters, same manual control values, same mode."""
    module = make_module()
    default_snapshot = module.get_persistence_snapshot()

    module.apply_persistence_snapshot(default_snapshot)

    assert module.get_persistence_snapshot().control_mode == "manual"
    assert module.get_persistence_snapshot().parameters == default_snapshot.parameters
    assert (
        module.get_persistence_snapshot().manual_control_values
        == default_snapshot.manual_control_values
    )


def test_apply_snapshot_with_unchanged_values_does_not_crash_with_debug_logging(
    caplog: pytest.LogCaptureFixture,
):
    """Regression test: applying a snapshot used to crash with
    `AttributeError: 'ModulePersistenceSnapshot' object has no attribute 'diff'`
    whenever DEBUG logging was enabled, because the debug log line called
    `snapshot.diff(...)` before that method existed. Same default values in, same
    values out - only the diff log should fire, nothing should raise."""
    caplog.set_level(logging.DEBUG, logger="thrs.orchestration.module")
    module = make_module()
    default_snapshot = module.get_persistence_snapshot()

    module.apply_persistence_snapshot(default_snapshot)

    assert "differing from hardcoded defaults" in caplog.text
    assert "(matches defaults)" in caplog.text


async def test_persist_then_restore_reproduces_the_module_snapshot():
    channels = make_channels()
    channels.get_parameters.return_value = ConfigurableParameters(setpoint=65.0)
    channels.get_manual_controls.return_value = manual_values(1.25)
    channels.get_automation_modes.return_value = AutomationMode(mode="automatic")

    store = InMemoryPersistentEngine()
    running = make_module(channels=channels)
    await running.sync_control_channels_state()
    await PersistManager(store).persist(running)

    restarted = make_module()
    restored = await PersistManager(store).restore(restarted)

    assert restored is True
    assert restarted.get_persistence_snapshot() == running.get_persistence_snapshot()
