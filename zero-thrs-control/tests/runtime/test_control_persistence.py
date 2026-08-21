from typing import cast
from unittest import mock

from thrs.classes.persistence.engine import (
    InMemoryPersistentEngine,
    NoopPersistentEngine,
)
from thrs.classes.persistence.manager import PersistManager
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.orchestration.module import Module
from thrs.runtime.liveness import Liveness
from thrs.runtime.runners.control import ControlRunner


def make_module(name: str, snapshot: ModulePersistenceSnapshot) -> mock.AsyncMock:
    module = mock.AsyncMock()
    module.name = name
    module.sync_control_channels_state.return_value = None
    module.get_persistence_snapshot = mock.Mock(return_value=snapshot)
    return module


def make_runner(
    modules: list[mock.AsyncMock], store: InMemoryPersistentEngine
) -> ControlRunner:
    persistence = PersistManager(store)
    return ControlRunner(
        cast(list[Module], modules), mock.Mock(spec=Liveness), persistence
    )


async def test_control_runner_persists_module_snapshot_on_tick():
    store = InMemoryPersistentEngine()
    snapshot = ModulePersistenceSnapshot(parameters={"setpoint": 55.0})
    runner = make_runner([make_module("dhw", snapshot)], store)

    await runner.tick()

    assert store.snapshots["dhw"] == snapshot


async def test_control_runner_does_not_rewrite_unchanged_snapshot():
    store = InMemoryPersistentEngine()
    store.save = mock.AsyncMock(wraps=store.save)
    runner = make_runner([make_module("dhw", ModulePersistenceSnapshot())], store)

    await runner.tick()
    await runner.tick()

    assert store.save.await_count == 1
    assert store.snapshots["dhw"] == ModulePersistenceSnapshot()


async def test_control_runner_runs_with_persistence_disabled():
    """`module_persistence` off in the CLI still wires up a PersistManager, backed by
    a no-op engine - the runner never has to special-case a missing persistence
    manager."""
    module = make_module("dhw", ModulePersistenceSnapshot())
    persistence = PersistManager(NoopPersistentEngine())
    runner = ControlRunner(
        cast(list[Module], [module]), mock.Mock(spec=Liveness), persistence
    )

    await runner.tick()

    assert module.tick.await_count == 1
