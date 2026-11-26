from datetime import timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from tests.helpers.modules import ConfigurableControllerState, ConfigurableParameters
from thrs.classes.persistence.engine import (
    InMemoryPersistentEngine,
    NoopPersistentEngine,
    PersistentEngine,
)
from thrs.classes.persistence.manager import PersistManager
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.control.state import AutomationMode, ControlModes

HEARTBEAT = timedelta(seconds=60)


class FailingSnapshotStore(PersistentEngine):
    def _error(self) -> OperationalError:
        return OperationalError("select 1", {}, Exception("connection refused"))

    async def load(self, module_name: str) -> ModulePersistenceSnapshot | None:
        raise self._error()

    async def save(self, module_name: str, snapshot: ModulePersistenceSnapshot) -> None:
        raise self._error()


class CorruptSnapshotStore(PersistentEngine):
    """Simulates a real `PostgresPersistentEngine` hitting a row with an
    unrecognized `automation_mode` - the snapshot construction itself raises."""

    async def load(self, module_name: str) -> ModulePersistenceSnapshot | None:
        return ModulePersistenceSnapshot.model_validate(
            {"parameters": None, "control_mode": "x"}
        )

    async def save(self, module_name: str, snapshot: ModulePersistenceSnapshot) -> None:
        raise NotImplementedError


def controller_state(
    setpoint: float = 50.0, mode: ControlModes = "manual"
) -> ConfigurableControllerState:
    return ConfigurableControllerState(
        parameters=ConfigurableParameters(setpoint=setpoint),
        automation_mode=AutomationMode(mode=mode),
    )


def test_snapshot_takes_parameters_and_mode_from_the_controller_state():
    snapshot = ModulePersistenceSnapshot.from_controller_state(
        controller_state(60.0, "automatic")
    )

    assert snapshot == ModulePersistenceSnapshot(
        parameters={"setpoint": 60.0}, control_mode="automatic"
    )


async def test_persist_writes_on_first_call():
    store = InMemoryPersistentEngine()
    manager = PersistManager(store, HEARTBEAT)

    assert await manager.persist("test", controller_state()) is True
    assert store.snapshots["test"] == ModulePersistenceSnapshot(
        parameters={"setpoint": 50.0}, control_mode="manual"
    )


async def test_persist_skips_unchanged_snapshot():
    manager = PersistManager(InMemoryPersistentEngine(), HEARTBEAT)

    assert await manager.persist("test", controller_state()) is True
    assert await manager.persist("test", controller_state()) is False


async def test_persist_writes_when_config_changes():
    store = InMemoryPersistentEngine()
    manager = PersistManager(store, HEARTBEAT)

    assert await manager.persist("test", controller_state(50.0)) is True
    assert await manager.persist("test", controller_state(60.0)) is True
    assert store.snapshots["test"].parameters == {"setpoint": 60.0}


async def test_load_without_stored_config_returns_none():
    manager = PersistManager(InMemoryPersistentEngine(), HEARTBEAT)

    assert await manager.load("test") is None


async def test_load_returns_the_stored_snapshot():
    stored = ModulePersistenceSnapshot(
        parameters={"setpoint": 60.0}, control_mode="automatic"
    )
    manager = PersistManager(InMemoryPersistentEngine({"test": stored}), HEARTBEAT)

    assert await manager.load("test") == stored


async def test_a_loaded_snapshot_is_not_written_back_unchanged():
    stored = ModulePersistenceSnapshot(parameters={"setpoint": 60.0})
    store = InMemoryPersistentEngine({"test": stored})
    manager = PersistManager(store, HEARTBEAT)

    await manager.load("test")

    assert await manager.persist("test", controller_state(60.0)) is False
    assert store.snapshots["test"] == stored


async def test_load_raises_on_a_corrupt_row():
    manager = PersistManager(CorruptSnapshotStore(), HEARTBEAT)

    with pytest.raises(ValidationError):
        await manager.load("test")


async def test_database_errors_propagate_from_load_and_persist():
    manager = PersistManager(FailingSnapshotStore(), HEARTBEAT)

    with pytest.raises(OperationalError):
        await manager.load("test")

    with pytest.raises(OperationalError):
        await manager.persist("test", controller_state())


async def test_failed_write_is_retried_next_call():
    manager = PersistManager(FailingSnapshotStore(), HEARTBEAT)

    with pytest.raises(OperationalError):
        await manager.persist("test", controller_state())

    assert manager._persisted == {}


async def test_noop_store_never_returns_a_snapshot():
    store = NoopPersistentEngine()
    manager = PersistManager(store, HEARTBEAT)

    assert await manager.load("test") is None
    assert await manager.persist("test", controller_state()) is True
    assert await store.load("test") is None
