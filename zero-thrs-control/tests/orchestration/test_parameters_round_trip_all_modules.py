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

from tests.helpers.modules import make_async_channels
from thrs.control.modules.adsorption.control import ADSORPTION_MODULE_DESCRIPTION
from thrs.control.modules.consumers.control import CONSUMERS_MODULE_DESCRIPTION
from thrs.control.modules.dc.control import DC_MODULE_DESCRIPTION
from thrs.control.modules.dhw.control import DHW_MODULE_DESCRIPTION
from thrs.control.modules.drives.control import DRIVES_MODULE_DESCRIPTION
from thrs.control.modules.pcm.control import PCM_MODULE_DESCRIPTION
from thrs.control.modules.pvt.control import PVT_MODULE_DESCRIPTION
from thrs.control.modules.thrusters.control import THRUSTERS_MODULE_DESCRIPTION
from thrs.orchestration.comms import MqttConnector
from thrs.orchestration.config import Config
from thrs.orchestration.module import Module, ModuleDescription
from thrs.orchestration.setup import setup_control_modules
from thrs.persistence.engine import InMemoryPersistentEngine
from thrs.persistence.manager import PersistManager

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


@pytest.mark.parametrize("name,description", ALL_MODULE_DESCRIPTIONS.items())
async def test_changed_parameter_is_stored_and_restored(
    settings: Config, name: str, description: ModuleDescription
):
    defaults = description.parameters_cls()
    changed = _changed_from_defaults(description.parameters_cls)
    assert changed.model_dump() != defaults.model_dump(), (
        "the mutated parameters must actually differ from the defaults, "
        "otherwise this test proves nothing"
    )

    store = InMemoryPersistentEngine()
    manager = PersistManager(store)

    module = Module(
        name,
        description=description,
        channels=make_async_channels(),
        time_fn=lambda: datetime.now(UTC),
        parameters=changed,
    )

    _, state = await module.tick(None)
    assert await manager.persist(name, state) is True
    assert store.snapshots[name].parameters == changed.model_dump(mode="json")

    # Fresh modules and a fresh manager, as if the process had restarted - the
    # only thing carrying state across is the (in-memory, here) database.
    [restarted_module] = await setup_control_modules(
        MqttConnector(mock.AsyncMock()),
        settings,
        {name: description},
        lambda: datetime.now(UTC),
        PersistManager(store),
    )

    _, restored_state = await restarted_module.tick(None)
    assert restored_state.parameters == changed
    assert restored_state.parameters != defaults
