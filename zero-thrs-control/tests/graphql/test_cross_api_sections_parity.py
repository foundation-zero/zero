"""Cross-API parity for the *whole module view* the UI reads: not just
``sensorValues`` (covered exhaustively in ``test_cross_api_parity_exhaustive``)
but the other three sections zero-ui queries next to it -
``modules.<module>.{controlValues, parameters, controllerState}`` (zero-ui
thrsim ``*_CONTROL_QUERY`` / ``*_PARAMETERS_QUERY`` /
``*_CONTROLLER_STATE_QUERY``).

The migration goal is that zero-mqtt-graphql (5103) can replace thrs-api (5102)
for the UI, so every section must return equal data. Unlike sensorValues (one
MQTT topic per field), each of these sections is one whole object published on a
single controller topic (``manual-values`` / ``parameters`` /
``controller-state``); mqtt-graphql reads the object from the cache and pulls
each field out by its by-alias wire key. Where the controller hasn't published a
section both services return null - still equal, still asserted.

Selections come from ``build_module_view`` (the same spec mqtt-graphql serves,
derived from the pydantic models so it can't drift from the UI's shape), so a new
field is covered the moment it appears on a model.

Computed sensor fields only match when mqtt-graphql recomputes them
(``COMPUTED_MODE=recompute``, see ``COMPUTED_IN_SCOPE``): thrs-api derives them
live, while in relay mode mqtt-graphql serves what the control loop published.

Run from ``zero-thrs-control/`` with the stack up::

    uv run pytest tests/graphql/test_cross_api_sections_parity.py
"""

from __future__ import annotations

import math
import os
from datetime import datetime
from typing import Any

import httpx
import pytest

from thrs.spec.asyncapi import all_module_descriptions, build_module_view

THRS_API_URL = "http://localhost:5102/graphql"
MQTT_GRAPHQL_URL = "http://localhost:5103/graphql"

# Modules whose nested view is verified 1:1 on mqtt-graphql. All of them: pvt's
# snake->camel collision is resolved in the spec (the shadowed field is
# `inputOnly` and never selected here).
MQTT_GRAPHQL_READY_MODULES: frozenset[str] = frozenset(
    {"adsorption", "consumers", "dc", "dhw", "drives", "pcm", "pvt", "thrusters"}
)

MODULES = sorted(all_module_descriptions())

# Computed sensor fields only match when mqtt-graphql recomputes them
# (COMPUTED_MODE=recompute) instead of relaying the loop's (possibly stale)
# published value. The computed parity test therefore runs only when the stack
# is in recompute mode (set COMPUTED_MODE=recompute in this test's environment to
# match the running container), and only for modules whose formulas are ported.
COMPUTED_IN_SCOPE = os.environ.get("COMPUTED_MODE") == "recompute"
RECOMPUTE_READY_MODULES: frozenset[str] = frozenset({"thrusters", "dhw", "pvt"})
FLOAT_REL_TOL = 1e-9


def _query(url: str, query: str) -> dict[str, Any]:
    response = httpx.post(url, json={"query": query}, timeout=20.0)
    response.raise_for_status()
    body = response.json()
    assert "errors" not in body, f"GraphQL errors from {url}: {body.get('errors')}"
    return body["data"]["modules"]


# Some computed fields carry a read-time ``now()`` timestamp (thrs-api's
# ``Stamped.stamp(0)`` for a heat-transfer device whose valve gate is off), so the
# same field's timestamp differs between two reads of thrs-api *itself*. Comparing
# those exactly is testing non-determinism; instead the computed suite allows the
# two services' timestamps to differ by up to this many seconds. Deterministic
# computed fields (which carry input timestamps) still agree to the second, so
# this only tolerates the inherent ``now()`` jitter, not real staleness (minutes).
COMPUTED_TS_TOL_S = 30.0


def _parse_ts(s: Any) -> datetime | None:
    if not isinstance(s, str):
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _values_equal(a: Any, b: Any, *, ts_tol_s: float = 0.0) -> bool:
    """Deep parity compare. Floats agree within ``FLOAT_REL_TOL`` (Python and
    Rust format f64s differently - a 1-ULP display artifact, not a data
    difference). Timestamps compare exactly unless ``ts_tol_s`` is set, in which
    case two ISO-8601 timestamps may differ by up to that many seconds (for the
    computed ``now()`` fields, see ``COMPUTED_TS_TOL_S``); everything else
    compares exactly."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(
            _values_equal(a[k], b[k], ts_tol_s=ts_tol_s) for k in a
        )
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(
            _values_equal(x, y, ts_tol_s=ts_tol_s) for x, y in zip(a, b)
        )
    if isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=FLOAT_REL_TOL, abs_tol=1e-12)
    # int vs float from the two encoders (25 vs 25.0) is still the same number.
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(float(a), float(b), rel_tol=FLOAT_REL_TOL, abs_tol=1e-12)
    if ts_tol_s:
        ta, tb = _parse_ts(a), _parse_ts(b)
        if ta is not None and tb is not None:
            return abs((ta - tb).total_seconds()) <= ts_tol_s
    return a == b


def _leaf_selection(leaves: list[dict[str, Any]]) -> str:
    return " ".join(f"{leaf['gql']} {{ value timestamp }}" for leaf in leaves)


def _object_section_selection(section: dict[str, Any]) -> str:
    """A GraphQL selection for a whole-object section: flat fields select the
    scalar directly, component fields select their `{value timestamp}` leaves."""
    parts = []
    for field in section["fields"]:
        if field.get("leaves"):
            parts.append(
                f"{field['gqlField']} {{ {_leaf_selection(field['leaves'])} }}"
            )
        else:
            parts.append(field["gqlField"])
    return " ".join(parts)


def _sensor_selection(entries: list[dict[str, Any]], *, computed: bool) -> str:
    # `inputOnly` entries are snake->camel collision shadows that thrs-api serves
    # no query field for (mqtt-graphql keeps them only as recompute inputs), so
    # never select them - thrs-api would 400 on the unknown field.
    parts = [
        f"{e['gqlField']} {{ {_leaf_selection(e['leaves'])} }}"
        for e in entries
        if bool(e.get("computed")) == computed and not e.get("inputOnly")
    ]
    return " ".join(parts)


OBJECT_SECTIONS = ("controlValues", "parameters", "controllerState")


@pytest.mark.parametrize("module", MODULES)
@pytest.mark.parametrize("section_name", OBJECT_SECTIONS)
def test_object_section_parity(module: str, section_name: str) -> None:
    """controlValues / parameters / controllerState return equal data (or equal
    null) from both APIs for every ready module."""
    if module not in MQTT_GRAPHQL_READY_MODULES:
        pytest.skip(f"{module} not yet verified on mqtt-graphql")
    view = build_module_view(module)
    section = view[section_name]
    selection = _object_section_selection(section)
    if not selection:
        pytest.skip(f"{module}.{section_name} has no fields")
    query = f"{{ modules {{ {module} {{ {section_name} {{ {selection} }} }} }} }}"
    thrs_api = _query(THRS_API_URL, query)[module][section_name]
    mqtt_graphql = _query(MQTT_GRAPHQL_URL, query)[module][section_name]
    assert _values_equal(thrs_api, mqtt_graphql), (
        f"{module}.{section_name} differs:\n thrs-api={thrs_api}\n mqtt={mqtt_graphql}"
    )


@pytest.mark.parametrize("module", MODULES)
def test_sensor_values_raw_parity(module: str) -> None:
    """Raw (non-computed) sensorValues return equal data from both APIs."""
    if module not in MQTT_GRAPHQL_READY_MODULES:
        pytest.skip(f"{module} not yet verified on mqtt-graphql")
    view = build_module_view(module)
    selection = _sensor_selection(view["sensorValues"], computed=False)
    if not selection:
        pytest.skip(f"{module} has no raw sensor fields")
    query = f"{{ modules {{ {module} {{ sensorValues {{ {selection} }} }} }} }}"
    thrs_api = _query(THRS_API_URL, query)[module]["sensorValues"]
    mqtt_graphql = _query(MQTT_GRAPHQL_URL, query)[module]["sensorValues"]
    assert _values_equal(thrs_api, mqtt_graphql), (
        f"{module}.sensorValues (raw) differs:\n thrs-api={thrs_api}\n mqtt={mqtt_graphql}"
    )


@pytest.mark.skipif(
    not COMPUTED_IN_SCOPE,
    reason="run with COMPUTED_MODE=recompute against a recompute stack",
)
@pytest.mark.parametrize("module", MODULES)
def test_sensor_values_computed_parity(module: str) -> None:
    """Computed sensorValues parity when mqtt-graphql recomputes them: it derives
    the same value from the same raw sensors, so it matches thrs-api's live
    value (and its min-combined timestamp). Only ported modules are asserted."""
    if module not in RECOMPUTE_READY_MODULES:
        pytest.skip(f"{module} computed fields not yet ported to recompute")
    if module not in MQTT_GRAPHQL_READY_MODULES:
        pytest.skip(f"{module} not yet verified on mqtt-graphql")
    view = build_module_view(module)
    selection = _sensor_selection(view["sensorValues"], computed=True)
    if not selection:
        pytest.skip(f"{module} has no computed sensor fields")
    query = f"{{ modules {{ {module} {{ sensorValues {{ {selection} }} }} }} }}"
    thrs_api = _query(THRS_API_URL, query)[module]["sensorValues"]
    mqtt_graphql = _query(MQTT_GRAPHQL_URL, query)[module]["sensorValues"]
    assert _values_equal(thrs_api, mqtt_graphql, ts_tol_s=COMPUTED_TS_TOL_S), (
        f"{module}.sensorValues (computed) differs:\n"
        f" thrs-api={thrs_api}\n mqtt={mqtt_graphql}"
    )
