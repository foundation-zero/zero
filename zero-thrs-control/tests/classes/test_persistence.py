import logging
from datetime import timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from tests.helpers.modules import (
    ConfigurableModule,
    make_async_channels,
    make_module,
    manual_values,
)
from tests.orchestration.simples import SimpleInOut
from thrs.classes.persistence.engine import (
    InMemoryPersistentEngine,
    NoopPersistentEngine,
    PersistentEngine,
)
from thrs.classes.persistence.manager import PersistManager
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot

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
            {"parameters": None, "manual_control_values": None, "control_mode": "x"}
        )

    async def save(self, module_name: str, snapshot: ModulePersistenceSnapshot) -> None:
        raise NotImplementedError


def make_manager(
    store: PersistentEngine, apply_module_defaults_on_corrupt_database: bool = False
) -> PersistManager:
    return PersistManager(store, HEARTBEAT, apply_module_defaults_on_corrupt_database)


def change_setpoint(module: ConfigurableModule, setpoint: float) -> None:
    module.apply_persistence_snapshot(
        ModulePersistenceSnapshot(parameters={"setpoint": setpoint})
    )


def test_diff_is_empty_for_identical_snapshots():
    snapshot = ModulePersistenceSnapshot(
        parameters={"setpoint": 50.0},
        manual_control_values={"dhw_pump": {"on": {"value": False}}},
        control_mode="manual",
    )

    assert snapshot.diff(snapshot.model_copy(deep=True)) == {}


def test_diff_reports_only_the_changed_leaf_by_dotted_path():
    old = ModulePersistenceSnapshot(
        manual_control_values={
            "dhw_pump": {
                "on": {"value": False, "timestamp": "2026-08-24T12:10:00"},
                "dutypoint": {"value": 0.0, "timestamp": "2026-08-24T12:10:00"},
            }
        },
    )
    new = ModulePersistenceSnapshot(
        manual_control_values={
            "dhw_pump": {
                "on": {"value": True, "timestamp": "2026-08-24T12:29:00"},
                "dutypoint": {"value": 0.0, "timestamp": "2026-08-24T12:29:00"},
            }
        },
    )

    diff = old.diff(new)

    assert diff == {
        "manual_control_values.dhw_pump.on.value": (False, True),
        "manual_control_values.dhw_pump.on.timestamp": (
            "2026-08-24T12:10:00",
            "2026-08-24T12:29:00",
        ),
        "manual_control_values.dhw_pump.dutypoint.timestamp": (
            "2026-08-24T12:10:00",
            "2026-08-24T12:29:00",
        ),
    }


async def test_persist_writes_on_first_call():
    store = InMemoryPersistentEngine()
    manager = make_manager(store)
    module = make_module()

    assert await manager.persist(module) is True
    assert store.snapshots["dhw"] == module.get_persistence_snapshot()


async def test_persist_skips_unchanged_snapshot():
    store = InMemoryPersistentEngine()
    manager = make_manager(store)
    module = make_module()

    assert await manager.persist(module) is True

    assert await manager.persist(module) is False
    assert store.snapshots["dhw"] == module.get_persistence_snapshot()


async def test_persist_skips_snapshot_that_only_changed_timestamps():
    """A re-published manual control value with the same value but a fresher
    Stamped timestamp (e.g. a dashboard re-sending the current setpoint) must
    not be treated as a config change - only actual value changes should."""
    store = InMemoryPersistentEngine()
    manager = make_manager(store)
    channels = make_async_channels()
    channels.get_manual_controls.side_effect = lambda: manual_values(3.5)
    module = make_module(channels=channels)
    await module.sync_control_channels_state()

    assert await manager.persist(module) is True

    # Re-sync with the identical value - `manual_values` re-stamps on every call.
    await module.sync_control_channels_state()

    assert await manager.persist(module) is False


async def test_persist_writes_when_config_changes():
    store = InMemoryPersistentEngine()
    manager = make_manager(store)
    module = make_module()

    assert await manager.persist(module) is True
    change_setpoint(module, 60.0)

    assert await manager.persist(module) is True
    assert store.snapshots["dhw"].parameters == {"setpoint": 60.0}


async def test_persist_all_covers_every_module():
    store = InMemoryPersistentEngine()
    manager = make_manager(store)

    await manager.persist_all([make_module("dhw"), make_module("pvt")])

    assert set(store.snapshots) == {"dhw", "pvt"}


async def test_restore_without_stored_config_keeps_defaults():
    manager = make_manager(InMemoryPersistentEngine())
    module = make_module()

    assert await manager.restore(module) is False
    assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}


async def test_restore_applies_stored_snapshot():
    stored = ModulePersistenceSnapshot(
        parameters={"setpoint": 60.0},
        control_mode="automatic",
    )
    manager = make_manager(InMemoryPersistentEngine({"dhw": stored}))
    module = make_module()

    assert await manager.restore(module) is True
    assert module.get_persistence_snapshot().parameters == {"setpoint": 60.0}
    assert module.get_persistence_snapshot().control_mode == "automatic"


async def test_restore_does_not_trigger_an_immediate_rewrite():
    stored = ModulePersistenceSnapshot(parameters={"setpoint": 60.0})
    store = InMemoryPersistentEngine({"dhw": stored})
    manager = make_manager(store)
    module = make_module()

    await manager.restore(module)

    assert await manager.persist(module) is False
    assert store.snapshots["dhw"] == stored


async def test_restore_all_covers_every_module():
    store = InMemoryPersistentEngine(
        {"dhw": ModulePersistenceSnapshot(control_mode="automatic")}
    )
    manager = make_manager(store)
    modules = [make_module("dhw"), make_module("pvt")]

    await manager.restore_all(modules)

    assert modules[0].get_persistence_snapshot().control_mode == "automatic"
    assert modules[1].get_persistence_snapshot().control_mode == "manual"


async def test_restore_keeps_defaults_when_stored_config_no_longer_validates():
    store = InMemoryPersistentEngine(
        {"dhw": ModulePersistenceSnapshot(parameters={"setpoint": "warm"})}
    )
    manager = make_manager(store)
    module = make_module()

    assert await manager.restore(module) is False
    assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}


async def test_database_errors_do_not_break_the_control_loop():
    manager = make_manager(FailingSnapshotStore())
    module = make_module()

    assert await manager.restore(module) is False
    assert await manager.persist(module) is False


async def test_corrupt_stored_snapshot_raises_by_default():
    """`apply_module_defaults_on_corrupt_database` defaults to False - a corrupt row
    must surface loudly (raise) rather than silently fall back to defaults."""
    manager = make_manager(CorruptSnapshotStore())
    module = make_module()

    with pytest.raises(ValidationError):
        await manager.restore(module)


async def test_corrupt_stored_snapshot_keeps_defaults_instead_of_crashing(
    caplog: pytest.LogCaptureFixture,
):
    """With `apply_module_defaults_on_corrupt_database=True`, a row with an
    unrecognized `automation_mode` (e.g. hand-edited) must degrade that single
    module to its defaults and log it - never crash `restore_all` for every other
    module."""
    caplog.set_level(logging.ERROR, logger="thrs.classes.persistence.manager")
    manager = make_manager(
        CorruptSnapshotStore(), apply_module_defaults_on_corrupt_database=True
    )
    module = make_module()

    assert await manager.restore(module) is False
    assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}
    assert "corrupt" in caplog.text


async def test_restore_all_survives_one_module_with_a_corrupt_snapshot():
    manager = make_manager(
        CorruptSnapshotStore(), apply_module_defaults_on_corrupt_database=True
    )
    modules = [make_module("dhw"), make_module("pvt")]

    await manager.restore_all(modules)

    for module in modules:
        assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}


async def test_restore_all_stops_on_first_corrupt_snapshot_by_default():
    """Without opting in, one corrupt module must abort `restore_all` rather than
    silently skipping it and continuing to the next module."""
    manager = make_manager(CorruptSnapshotStore())
    modules = [make_module("dhw"), make_module("pvt")]

    with pytest.raises(ValidationError):
        await manager.restore_all(modules)


async def test_failed_write_is_retried_next_call():
    manager = make_manager(FailingSnapshotStore())

    await manager.persist(make_module())

    assert manager._persisted_at == {}


async def test_noop_store_never_returns_a_snapshot():
    store = NoopPersistentEngine()
    manager = make_manager(store)
    module = make_module()

    assert await manager.restore(module) is False
    assert await manager.persist(module) is True
    assert await store.load("dhw") is None


# --- Excessive / adversarial input handling -----------------------------------
#
# A corrupt or malicious row in the persistence store must never end up applied to
# a running module and, in turn, must never be published over MQTT. These tests
# feed obviously wrong data through `restore()` and prove the module keeps its safe
# defaults end-to-end, including through a real `tick()` that would otherwise send
# values out over the control channels.


@pytest.mark.parametrize(
    "bad_parameters",
    [
        pytest.param({"setpoint": 1_000_000.0}, id="wildly-out-of-bound-high"),
        pytest.param({"setpoint": -1_000_000.0}, id="wildly-out-of-bound-low"),
        pytest.param({"setpoint": float("inf")}, id="infinity"),
        pytest.param({"setpoint": float("-inf")}, id="negative-infinity"),
        pytest.param({"setpoint": float("nan")}, id="nan"),
        pytest.param({"setpoint": "warm"}, id="wrong-type-string"),
        pytest.param({"setpoint": None}, id="wrong-type-none"),
        pytest.param({"setpoint": [1, 2, 3]}, id="wrong-type-list"),
        pytest.param({"setpoint": {"nested": True}}, id="wrong-type-dict"),
        pytest.param({}, id="missing-field-falls-back-to-default"),
        pytest.param({"unexpected_field": "surprise"}, id="unknown-extra-field-only"),
    ],
)
async def test_restore_rejects_or_safely_ignores_bad_parameters(bad_parameters):
    stored = ModulePersistenceSnapshot(parameters=bad_parameters)
    manager = make_manager(InMemoryPersistentEngine({"dhw": stored}))
    module = make_module()

    await manager.restore(module)

    # Whatever happened, the module must never end up holding a value outside its
    # declared bounds.
    parameters = module.get_persistence_snapshot().parameters
    assert parameters is not None
    assert 0.0 <= parameters["setpoint"] <= 100.0


async def test_restore_with_out_of_bound_value_never_reaches_mqtt():
    """The most important guarantee: a corrupt snapshot must not leak into a control
    tick's outgoing MQTT payload."""
    stored = ModulePersistenceSnapshot(parameters={"setpoint": 1_000_000.0})
    manager = make_manager(InMemoryPersistentEngine({"dhw": stored}))
    channels = make_async_channels()
    module = make_module(channels=channels)

    assert await manager.restore(module) is False

    await module.tick(SimpleInOut.zero())

    sent_parameters = channels.send_parameters.call_args.args[0]
    assert sent_parameters.setpoint == 50.0


async def test_restore_with_malformed_control_mode_keeps_module_untouched():
    """A snapshot bypassing normal validation (e.g. a hand-edited or truncated DB
    row) must not be able to smuggle an unrecognized control mode into the module."""
    corrupt = ModulePersistenceSnapshot.model_construct(
        parameters={"setpoint": 60.0},
        manual_control_values=None,
        control_mode="deleted-enum-value",  # type: ignore[arg-type]
    )
    manager = make_manager(InMemoryPersistentEngine({"dhw": corrupt}))
    module = make_module()

    assert await manager.restore(module) is False
    assert module.get_persistence_snapshot().control_mode == "manual"
    assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}


async def test_restore_with_malformed_manual_control_values_keeps_defaults():
    corrupt = ModulePersistenceSnapshot(
        parameters={"setpoint": 60.0},
        manual_control_values={"go_with_the": "not-a-flow-sensor"},
    )
    manager = make_manager(InMemoryPersistentEngine({"dhw": corrupt}))
    module = make_module()

    assert await manager.restore(module) is False
    # Since manual control values fail validation, the whole restore is rejected -
    # even the otherwise-valid setpoint must not be partially applied.
    assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}


async def test_excessive_bad_snapshots_across_many_modules_never_crash_the_loop():
    """Simulates a fleet of modules with every kind of corrupted row at once - the
    manager must degrade every one of them to safe defaults, never raise, and never
    take down `restore_all`."""
    bad_values = [
        1_000_000.0,
        -1_000_000.0,
        float("inf"),
        float("-inf"),
        float("nan"),
        "warm",
        None,
    ]
    store = InMemoryPersistentEngine(
        {
            f"module-{i}": ModulePersistenceSnapshot(parameters={"setpoint": value})
            for i, value in enumerate(bad_values)
        }
    )
    manager = make_manager(store)
    modules = [make_module(f"module-{i}") for i in range(len(bad_values))]

    await manager.restore_all(modules)

    for module in modules:
        assert module.get_persistence_snapshot().parameters == {"setpoint": 50.0}
