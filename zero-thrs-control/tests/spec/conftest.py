"""The spec is derived from the module descriptions as declared.

``setup_control_modules`` (orchestration/setup.py) wraps each description's
``control_mode_cls`` in ``SwitchingControlMode[...]`` *in place* on the shared
``MODES`` singletons, so any earlier test that runs the real setup in-process
(e.g. tests/cli) leaves them wrapped, and wrapped again on the next run. The
spec tests therefore restore the classes as they were at collection time,
before any test ran.
"""

import pytest

from thrs.orchestration.config import Config
from thrs.runtime.descriptions.simulation import MODES
from thrs.spec.asyncapi import TOPIC_SETTINGS

_DECLARED_CONTROL_MODE_CLASSES = {
    id(description): description.control_mode_cls
    for mode in MODES
    for description in mode.control_modules.values()
}


@pytest.fixture(autouse=True)
def declared_module_descriptions() -> None:
    for mode in MODES:
        for description in mode.control_modules.values():
            description.control_mode_cls = _DECLARED_CONTROL_MODE_CLASSES[
                id(description)
            ]


@pytest.fixture(scope="session")
def settings() -> Config:
    """A config with a distinct value for every setting the spec leaves open."""
    return Config.model_validate(
        {name: f"x-{name.removeprefix('mqtt_')}" for name in TOPIC_SETTINGS}
        | {"mqtt_host": "broker", "mqtt_port": 1883}
    )
