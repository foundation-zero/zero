"""Cross-API parity for the *whole module view* the UI reads: not just
``sensorValues`` (covered exhaustively in ``test_cross_api_parity_exhaustive``)
but the other three sections zero-ui queries next to it -
``modules.<module>.{controlValues, parameters, controllerState}`` (zero-ui
thrsim ``*_CONTROL_QUERY`` / ``*_PARAMETERS_QUERY`` /
``*_CONTROLLER_STATE_QUERY``).

zero-mqtt-graphql (5103) replaces thrs-api (5102) for the UI, so every section
must return equal data. Unlike sensorValues (one MQTT topic per field), each of
these sections is one whole object published on a single controller topic
(``manual-values`` / ``parameters`` / ``controller-state``); mqtt-graphql reads
the object from the cache and pulls each field out by its wire key. Where the
controller hasn't published a section both services return null - still equal,
still asserted.

Selections come from the contract (``tests.graphql.resolved``: the spec
mqtt-graphql serves, derived from the pydantic models so it can't drift from
the UI's shape), so a new field is covered the moment it appears on a model.

The suite seeds one complete state itself (``tests.graphql.seeding``), so the
control loop must not be ticking.

Computed sensor fields are relayed from the control loop by mqtt-graphql (opt in
with ``THRS_COMPUTED_PARITY=1``, see ``COMPUTED_IN_SCOPE``): thrs-api derives them
live, while mqtt-graphql serves what the control loop published.

Run from ``zero-thrs-control/`` with the stack up::

    uv run pytest tests/graphql/test_cross_api_sections_parity.py
"""

from __future__ import annotations

import os
from typing import Any

import pytest

from tests.graphql.parity import query_data, values_equal
from tests.graphql.resolved import ResolvedSpec, section_of
from tests.graphql.seeding import seed_state
from tests.graphql.stack_config import MQTT_GRAPHQL_URL, THRS_API_URL, thrs_api_config

pytestmark = pytest.mark.migration

CONTRACT = ResolvedSpec(thrs_api_config())
MODULES = sorted(CONTRACT.members)

# mqtt-graphql relays computed sensor fields from the controller topics the
# control loop publishes them on, while thrs-api derives them live from the raw
# sensors; the two only agree once the loop has published every computed field
# and hasn't lagged since. The computed parity test is therefore opt-in: set
# THRS_COMPUTED_PARITY=1 against a stack whose loop is ticking.
COMPUTED_IN_SCOPE = os.environ.get("THRS_COMPUTED_PARITY") == "1"

# Some computed fields carry a read-time ``now()`` timestamp (thrs-api's
# ``Stamped.stamp(0)`` for a heat-transfer device whose valve gate is off), so the
# same field's timestamp differs between two reads of thrs-api *itself*. Comparing
# those exactly is testing non-determinism; instead the computed suite allows the
# two services' timestamps to differ by up to this many seconds. Deterministic
# computed fields (which carry input timestamps) still agree to the second, so
# this only tolerates the inherent ``now()`` jitter, not real staleness (minutes).
COMPUTED_TS_TOL_S = 30.0

OBJECT_SECTIONS = ("controlValues", "parameters", "controllerState")


@pytest.fixture(scope="session", autouse=True)
def seeded_state(docker_stack: None) -> None:
    """Seed the complete state once (``tests.graphql.seeding``), so what the
    sections show does not depend on which suite ran before."""
    seed_state()


def _leaf_selection(leaves: list[dict[str, Any]]) -> str:
    return " ".join(f"{leaf['gql']} {{ value timestamp }}" for leaf in leaves)


def _object_section_selection(section: dict[str, Any]) -> str:
    """A GraphQL selection for a whole-object section: flat fields select the
    scalar directly, component fields select their `{value timestamp}` leaves."""
    parts = []
    for field in section["fields"]:
        if field.get("leaves"):
            parts.append(f"{field['gql']} {{ {_leaf_selection(field['leaves'])} }}")
        else:
            parts.append(field["gql"])
    return " ".join(parts)


def _sensor_selection(entries: list[dict[str, Any]], *, computed: bool) -> str:
    return " ".join(
        f"{e['gql']} {{ {_leaf_selection(e['leaves'])} }}"
        for e in entries
        if bool(e.get("computed")) == computed
    )


def _both(module: str, section_name: str, selection: str) -> tuple[Any, Any]:
    query = f"{{ modules {{ {module} {{ {section_name} {{ {selection} }} }} }} }}"
    return (
        query_data(THRS_API_URL, query)["modules"][module][section_name],
        query_data(MQTT_GRAPHQL_URL, query)["modules"][module][section_name],
    )


@pytest.mark.parametrize("module", MODULES)
@pytest.mark.parametrize("section_name", OBJECT_SECTIONS)
def test_object_section_parity(module: str, section_name: str) -> None:
    """controlValues / parameters / controllerState return equal data (or equal
    null) from both APIs for every module."""
    section = section_of(CONTRACT.members[module], section_name)
    selection = _object_section_selection(section)
    if not selection:
        pytest.skip(f"{module}.{section_name} has no fields")
    thrs_api, mqtt_graphql = _both(module, section_name, selection)
    assert values_equal(thrs_api, mqtt_graphql), (
        f"{module}.{section_name} differs:\n thrs-api={thrs_api}\n mqtt={mqtt_graphql}"
    )


@pytest.mark.parametrize("module", MODULES)
def test_sensor_values_raw_parity(module: str) -> None:
    """Raw (non-computed) sensorValues return equal data from both APIs."""
    fields = section_of(CONTRACT.members[module], "sensorValues")["fields"]
    selection = _sensor_selection(fields, computed=False)
    if not selection:
        pytest.skip(f"{module} has no raw sensor fields")
    thrs_api, mqtt_graphql = _both(module, "sensorValues", selection)
    assert values_equal(thrs_api, mqtt_graphql), (
        f"{module}.sensorValues (raw) differs:\n thrs-api={thrs_api}\n mqtt={mqtt_graphql}"
    )


@pytest.mark.skipif(
    not COMPUTED_IN_SCOPE,
    reason="opt in with THRS_COMPUTED_PARITY=1 against a stack whose loop is ticking",
)
@pytest.mark.parametrize("module", MODULES)
def test_sensor_values_computed_parity(module: str) -> None:
    """Computed sensorValues parity: mqtt-graphql relays the value the control
    loop published, thrs-api derives it live; with a ticking loop they match
    (timestamps within tolerance)."""
    fields = section_of(CONTRACT.members[module], "sensorValues")["fields"]
    selection = _sensor_selection(fields, computed=True)
    if not selection:
        pytest.skip(f"{module} has no computed sensor fields")
    thrs_api, mqtt_graphql = _both(module, "sensorValues", selection)
    assert values_equal(thrs_api, mqtt_graphql, ts_tol_s=COMPUTED_TS_TOL_S), (
        f"{module}.sensorValues (computed) differs:\n"
        f" thrs-api={thrs_api}\n mqtt={mqtt_graphql}"
    )
