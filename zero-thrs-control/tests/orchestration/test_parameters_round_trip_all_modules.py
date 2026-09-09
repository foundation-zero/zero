"""Persistence round-trip coverage across every real control module.

Regression coverage for the bug where a parameter change was logged as saved
(persistence log line written, `NoopPersistentEngine` never raising) while the
database row never actually changed, and separately where `lockstep` never
restored a previously persisted snapshot at startup. These tests exercise the
real `ModuleDescription`s (not the synthetic test module used elsewhere in this
test suite) end-to-end: change a parameter away from its hardcoded default,
persist it, restore it into a fresh module (simulating a process restart), and
assert the restored parameters match what was changed - not the defaults.
"""

from datetime import UTC, datetime
from unittest import mock

import pytest
from pydantic import ValidationError

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.classes.persistence.engine import InMemoryPersistentEngine
from thrs.classes.persistence.manager import PersistManager
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.control.modules.adsorption import ADSORPTION_MODULE_DESCRIPTION
from thrs.control.modules.consumers import CONSUMERS_MODULE_DESCRIPTION
from thrs.control.modules.dc import DC_MODULE_DESCRIPTION
from thrs.control.modules.dhw import DHW_MODULE_DESCRIPTION
from thrs.control.modules.drives import DRIVES_MODULE_DESCRIPTION
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION
from thrs.control.modules.thrusters import THRUSTERS_MODULE_DESCRIPTION
from thrs.orchestration.module import Module, ModuleDescription

ALL_MODULE_DESCRIPTIONS: dict[str, ModuleDescription] = {
    "adsorption": ADSORPTION_MODULE_DESCRIPTION,
    "consumers": CONSUMERS_MODULE_DESCRIPTION,
    "dc": DC_MODULE_DESCRIPTION,
    "dhw": DHW_MODULE_DESCRIPTION,
    "drives": DRIVES_MODULE_DESCRIPTION,
    "pcm": PCM_MODULE_DESCRIPTION,
    "pvt": PVT_MODULE_DESCRIPTION,
    "thrusters": THRUSTERS_MODULE_DESCRIPTION,
}


def _mutate(value):
    """Nudge a single scalar value to something different, without knowing the
    field's semantics up front - validity against the model is checked by the
    caller, which discards nudges that don't hold up."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 1.0
    if isinstance(value, str):
        return f"{value}_x"
    if isinstance(value, list):
        return [_mutate(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_mutate(v) for v in value)
    return value


def _changed_from_defaults(parameters_cls):
    """Build an instance of `parameters_cls` that differs from its hardcoded
    defaults in at least one field.

    Tries a nudge on every top-level field independently and keeps only the
    ones that still validate against the *whole* model - this safely skips
    fields guarded by cross-field validators (e.g. dhw's
    `minimum_tank_temperature < maximum_tank_temperature`) instead of having to
    know about them here.
    """
    values = parameters_cls().model_dump()
    changed_any = False

    for name, value in list(values.items()):
        candidate = _mutate(value)
        if candidate == value:
            continue

        trial = {**values, name: candidate}
        try:
            parameters_cls.model_validate(trial)
        except ValidationError:
            continue

        values = trial
        changed_any = True

    assert changed_any, (
        f"could not find a valid mutation for any field on {parameters_cls.__name__} - "
        "extend _mutate() or check the model's field types"
    )
    return parameters_cls.model_validate(values)


def _make_module(name: str, description: ModuleDescription) -> Module:
    """Build a real Module for `description`, with mocked control channels since
    we never send anything over MQTT in these tests - only persistence is under
    test here."""
    control = description.control(
        description.parameters_cls(),
        lambda: datetime.now(UTC),
        MachineStateLoggingServiceNoop(),
    )

    channels = mock.Mock()
    channels.get_sensor_values.return_value = None
    channels.get_parameters.return_value = None
    channels.get_manual_controls.return_value = None
    channels.get_automation_modes.return_value = None

    return Module(name, control, description.alarms(), channels)


@pytest.mark.parametrize("name,description", ALL_MODULE_DESCRIPTIONS.items())
async def test_changed_parameter_is_stored_and_restored(
    name: str, description: ModuleDescription
):
    defaults = description.parameters_cls()
    changed = _changed_from_defaults(description.parameters_cls)
    assert changed.model_dump() != defaults.model_dump(), (
        "the mutated parameters must actually differ from the defaults, "
        "otherwise this test proves nothing"
    )

    store = InMemoryPersistentEngine()
    manager = PersistManager(store)

    module = _make_module(name, description)
    module.apply_persistence_snapshot(
        ModulePersistenceSnapshot(parameters=changed.model_dump(mode="json"))
    )

    assert await manager.persist(module) is True
    assert store.snapshots[name].parameters == changed.model_dump(mode="json")

    # A fresh module and a fresh manager, as if the process had restarted - the
    # only thing carrying state across is the (in-memory, here) database.
    restarted_module = _make_module(name, description)
    restored = await PersistManager(store).restore(restarted_module)

    assert restored is True
    restored_parameters = restarted_module.get_persistence_snapshot().parameters
    assert restored_parameters == changed.model_dump(mode="json")
    assert restored_parameters != defaults.model_dump(mode="json")
