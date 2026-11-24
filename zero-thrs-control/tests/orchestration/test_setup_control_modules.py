from datetime import datetime
from unittest import mock

import pytest
from pydantic import ValidationError

from tests.helpers.modules import (
    CONFIGURABLE_MODULE_DESCRIPTION,
    ConfigurableParameters,
)
from thrs.control.state import AutomationMode
from thrs.orchestration.comms import MqttConnector
from thrs.orchestration.config import Config
from thrs.orchestration.module import Module
from thrs.orchestration.setup import setup_control_modules
from thrs.persistence.engine import InMemoryPersistentEngine
from thrs.persistence.manager import PersistManager
from thrs.persistence.module_snapshot import ModulePersistenceSnapshot

DEFAULTS = ConfigurableParameters()


async def build_module(
    settings: Config,
    stored: ModulePersistenceSnapshot | None = None,
) -> Module:
    store = InMemoryPersistentEngine({"test": stored} if stored is not None else {})
    [module] = await setup_control_modules(
        MqttConnector(mock.AsyncMock()),
        settings,
        {"test": CONFIGURABLE_MODULE_DESCRIPTION},
        datetime.now,
        PersistManager(store),
    )
    return module


async def test_a_module_without_stored_config_starts_from_defaults_in_manual(
    settings: Config,
):
    module = await build_module(settings)

    _, state = await module.tick(None)
    assert state.parameters == DEFAULTS
    assert state.automation_mode == AutomationMode(mode="manual")


async def test_a_module_starts_from_its_stored_config(settings: Config):
    stored = ModulePersistenceSnapshot(
        parameters={"setpoint": 60.0}, control_mode="automatic"
    )
    module = await build_module(settings, stored)

    _, state = await module.tick(None)
    assert state.parameters == ConfigurableParameters(setpoint=60.0)
    assert state.automation_mode == AutomationMode(mode="automatic")


# --- Excessive / adversarial input handling -----------------------------------
#
# A corrupt or malicious row in the persistence store must never end up in a
# running module, so it must never be published over MQTT either: building the
# module raises instead.


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
    ],
)
async def test_bad_stored_parameters_raise(settings: Config, bad_parameters):
    stored = ModulePersistenceSnapshot(parameters=bad_parameters)

    with pytest.raises(ValidationError):
        await build_module(settings, stored)


@pytest.mark.parametrize(
    "parameters",
    [
        pytest.param({}, id="missing-field-falls-back-to-default"),
        pytest.param({"unexpected_field": "surprise"}, id="unknown-extra-field-only"),
    ],
)
async def test_stored_parameters_that_validate_via_field_defaults_are_accepted(
    settings: Config, parameters
):
    """Missing fields fall back to the model's own default, and unrecognized extra
    fields are ignored - neither is a validation failure."""
    module = await build_module(
        settings, ModulePersistenceSnapshot(parameters=parameters)
    )

    _, state = await module.tick(None)
    assert state.parameters == DEFAULTS


async def test_a_malformed_stored_mode_raises(settings: Config):
    """A snapshot bypassing normal validation (e.g. a hand-edited or truncated DB
    row) must not be able to smuggle an unrecognized mode into the module."""
    corrupt = ModulePersistenceSnapshot.model_construct(
        parameters={"setpoint": 60.0},
        control_mode="deleted-enum-value",  # pyrefly: ignore[bad-argument-type]
    )

    with pytest.raises(ValidationError):
        await build_module(settings, corrupt)
