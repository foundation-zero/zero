"""The spec is derived from the module descriptions as declared.

``setup_control_modules`` (orchestration/setup.py) wraps each description's
``control_mode_cls`` in ``SwitchingControlMode[...]`` *in place* on the shared
``MODES`` singletons, so any earlier test that runs the real setup in-process
(e.g. tests/cli) leaves them wrapped, and wrapped again on the next run. The
spec tests therefore restore the classes as they were at collection time,
before any test ran.
"""

import pytest

from thrs.runtime.descriptions.simulation import MODES

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
