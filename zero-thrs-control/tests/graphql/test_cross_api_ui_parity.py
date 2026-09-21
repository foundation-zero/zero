"""UI-driven parity: the *exact* GraphQL documents zero-ui's thrsim module sends
to thrs-api must produce identical data from zero-mqtt-graphql.

The other cross-API suites are spec-driven (they enumerate what the specs
declare); this one is driven by the consumer. It reads zero-ui's documents
straight from its source (``stores/automation.ts`` ``CONTROL_QUERY``,
``stores/simulation.ts`` ``STATUS_QUERY``, ``lib/consts.ts`` ``QUERY_ALL`` with
its ``queries.generated.ts`` fragments), seeds one complete, deterministic state
on MQTT for both services (retained; both prefix sets), and asserts that thrs-api
(5102) and zero-mqtt-graphql (5103) answer each document with equal data.

It also asserts the schema surface the UI relies on by name: every mutation the
UI can build (``{module}{Control|Parameter|Simulation}Set{Component}``,
``{module}SetAutomationMode``, ``simulationPlay/Pause/Step``) with the same
argument and return types, and every ``<Component>InputType`` the UI hard-codes
as a variable type (``PumpInputType!``, ``[Float!]!``, ...), plus the enum
types they reference. Finally, the simulation directives' preconditions
(thrs-api's exact error strings) are compared without side effects.

Requires the docker stack (vernemq, thrs-api, mqtt-graphql). The control
loop must not be ticking (pause the simulation), or its publishes overwrite the
seeded state. Computed sensor fields are seeded the way the loop publishes them
(the controller topics mqtt-graphql relays); thrs-api computes them itself from
the seeded sensors.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from tests.graphql.parity import diff, post, query_data
from tests.graphql.seeding import seed_state
from tests.graphql.stack_config import MQTT_GRAPHQL_URL, THRS_API_URL
from thrs.spec import contract

pytestmark = pytest.mark.migration

# A few computed fields carry a ``now()`` timestamp (``Stamped.stamp(0)`` for
# a heat-transfer device whose valve gate is off): thrs-api stamps them at read
# time, the control loop (here: the seed) when it publishes them. Two such
# timestamps within this window of the wall clock count as equal; seeded
# timestamps still have to denote the same instant.
NOW_WINDOW_S = 60.0

UI_DIR = Path(__file__).resolve().parents[3] / "zero-ui" / "src" / "modules" / "thrsim"


# --- The UI's documents, read from its source ---------------------------------


def _ui_source(relative: str) -> str:
    path = UI_DIR / relative
    if not path.exists():
        pytest.skip(f"zero-ui source not found at {path}")
    return path.read_text(encoding="utf-8")


def ui_control_query() -> str:
    src = _ui_source("stores/automation.ts")
    return re.search(r"gql`\s*(query ControlStatus.*?)`", src, re.DOTALL).group(1)


def ui_status_query() -> str:
    src = _ui_source("stores/simulation.ts")
    return re.search(r"gql`\s*(query SimulationStatus.*?)`", src, re.DOTALL).group(1)


def ui_query_all() -> str:
    """Rebuild ``QUERY_ALL`` the way consts.ts does: substitute each
    ``${Queries.X}`` with the generated fragment, and expand
    ``${toUnionQueries(SIMULATION_*_QUERIES, toInputType/toOutputType)}`` into
    the ``... on <Key>Simulation<Inputs|Outputs>Type { __typename <fragment> }``
    members for every key of the map."""
    consts = _ui_source("lib/consts.ts")
    generated = _ui_source("lib/queries.generated.ts")
    fragments = {
        m.group(1): m.group(2)
        for m in re.finditer(r"export const (\w+) = `(.*?)`;", generated, re.DOTALL)
    }
    template = re.search(r"gql`\s*(query QueryAll.*?)`;", consts, re.DOTALL).group(1)

    def _map(name: str) -> list[tuple[str, str]]:
        body = re.search(
            rf"export const {name}[^=]*=\s*\{{(.*?)\}};", consts, re.DOTALL
        ).group(1)
        return re.findall(r"(\w+):\s*Queries\.(\w+)", body)

    def _union(map_name: str, suffix: str) -> str:
        return "\n".join(
            f"... on {key[0].upper()}{key[1:]}Simulation{suffix}Type {{ __typename {fragments[frag]} }}"
            for key, frag in _map(map_name)
        )

    template = template.replace(
        "${toUnionQueries(SIMULATION_INPUT_QUERIES, toInputType)}",
        _union("SIMULATION_INPUT_QUERIES", "Inputs"),
    ).replace(
        "${toUnionQueries(SIMULATION_OUTPUT_QUERIES, toOutputType)}",
        _union("SIMULATION_OUTPUT_QUERIES", "Outputs"),
    )
    return re.sub(r"\$\{Queries\.(\w+)\}", lambda m: fragments[m.group(1)], template)


@pytest.fixture(scope="session", autouse=True)
def seeded_state(docker_stack: None) -> None:
    """Seed once per session (``tests.graphql.seeding``)."""
    seed_state()


# --- Tests: the UI's read documents -------------------------------------------


@pytest.mark.parametrize(
    "document",
    ["ControlStatus", "SimulationStatus", "QueryAll"],
)
def test_ui_document_parity(document: str) -> None:
    """Each document the UI sends is accepted by both APIs and yields equal data."""
    query = {
        "ControlStatus": ui_control_query,
        "SimulationStatus": ui_status_query,
        "QueryAll": ui_query_all,
    }[document]()
    thrs_api = query_data(THRS_API_URL, query)
    mqtt_graphql = query_data(MQTT_GRAPHQL_URL, query)
    diffs = diff(thrs_api, mqtt_graphql, now_window_s=NOW_WINDOW_S)
    assert not diffs, f"{document}: {len(diffs)} difference(s):\n" + "\n".join(
        diffs[:60]
    )


def test_query_all_is_non_trivial() -> None:
    """Guard against a vacuous pass: the seeded state must actually surface
    (every module's sections non-null, simulation inputs typed)."""
    data = query_data(MQTT_GRAPHQL_URL, ui_query_all())
    for module, sections in data["modules"].items():
        for name, value in sections.items():
            assert value is not None, (
                f"{module}.{name} is null on mqtt-graphql after seeding"
            )
    assert data["simulation"]["inputs"]["__typename"] == "ThrustersSimulationInputsType"
    assert (
        data["simulation"]["outputs"]["__typename"] == "ThrustersSimulationOutputsType"
    )


# --- Tests: the schema surface the UI builds documents against ----------------

_TYPE_REF = "kind name ofType { kind name ofType { kind name ofType { kind name } } }"


def _type_str(t: dict[str, Any] | None) -> str:
    if t is None:
        return ""
    if t["kind"] == "NON_NULL":
        return _type_str(t["ofType"]) + "!"
    if t["kind"] == "LIST":
        return "[" + _type_str(t["ofType"]) + "]"
    return t["name"]


def _mutation_signatures(
    url: str,
) -> dict[str, tuple[str, tuple[tuple[str, str, Any], ...]]]:
    body = query_data(
        url,
        f'{{ __type(name: "Mutation") {{ fields {{ name type {{ {_TYPE_REF} }} '
        f"args {{ name defaultValue type {{ {_TYPE_REF} }} }} }} }} }}",
    )
    return {
        f["name"]: (
            _type_str(f["type"]),
            tuple(
                sorted(
                    (a["name"], _type_str(a["type"]), a["defaultValue"])
                    for a in f["args"]
                )
            ),
        )
        for f in body["__type"]["fields"]
    }


def _named_type(url: str, name: str) -> dict[str, Any] | None:
    body = query_data(
        url,
        f'{{ __type(name: "{name}") {{ kind name '
        f"inputFields {{ name defaultValue type {{ {_TYPE_REF} }} }} enumValues {{ name }} }} }}",
    )
    return body["__type"]


def test_ui_mutation_surface_parity() -> None:
    """Every mutation thrs-api exposes exists on mqtt-graphql with the same name,
    argument names/types/defaults and return type name - the UI composes
    ``{module}{Kind}Set{Component}``, ``{module}SetAutomationMode`` and the
    simulation directives by string, so nothing may be missing or renamed."""
    thrs_api = _mutation_signatures(THRS_API_URL)
    mqtt_graphql = _mutation_signatures(MQTT_GRAPHQL_URL)
    missing = sorted(set(thrs_api) - set(mqtt_graphql))
    assert not missing, f"mutations missing on mqtt-graphql: {missing}"
    extra = sorted(set(mqtt_graphql) - set(thrs_api))
    assert not extra, f"mutations only on mqtt-graphql: {extra}"
    differing = {
        n: (thrs_api[n], mqtt_graphql[n])
        for n in thrs_api
        if thrs_api[n] != mqtt_graphql[n]
    }
    assert not differing, f"mutation signatures differ: {differing}"


def test_ui_input_and_enum_types_parity() -> None:
    """The input types the UI hard-codes as variable types (``PumpInputType!``,
    ``PcsInputType!``, ...) and the enum types they reference are defined
    identically (fields, nullability, defaults, members) on both APIs."""
    thrs_api = _mutation_signatures(THRS_API_URL)
    input_names = sorted(
        {
            re.sub(r"[\[\]!]", "", arg_type)
            for _, args in thrs_api.values()
            for _, arg_type, _ in args
            if arg_type.endswith("InputType!")
        }
    )
    assert input_names, "thrs-api exposes no *InputType arguments?"
    seen_enums: set[str] = set()
    for name in input_names:
        a, b = _named_type(THRS_API_URL, name), _named_type(MQTT_GRAPHQL_URL, name)
        assert b is not None, f"input type {name} missing on mqtt-graphql"
        fa = sorted(
            (f["name"], _type_str(f["type"]), f["defaultValue"])
            for f in a["inputFields"]
        )
        fb = sorted(
            (f["name"], _type_str(f["type"]), f["defaultValue"])
            for f in b["inputFields"]
        )
        assert fa == fb, f"{name} differs:\n thrs-api={fa}\n mqtt-graphql={fb}"
        for _, t, _ in fa:
            base = re.sub(r"[\[\]!]", "", t)
            if base not in ("Float", "Int", "Boolean", "String"):
                seen_enums.add(base)
    for name in sorted(seen_enums):
        a, b = _named_type(THRS_API_URL, name), _named_type(MQTT_GRAPHQL_URL, name)
        assert b is not None and b["kind"] == "ENUM", (
            f"enum {name} missing on mqtt-graphql"
        )
        assert sorted(v["name"] for v in a["enumValues"]) == sorted(
            v["name"] for v in b["enumValues"]
        )


# --- Tests: simulation directives (side-effect free) --------------------------


def test_simulation_pause_precondition_parity() -> None:
    """With the simulation seeded ``available``, ``simulationPause`` (the UI's
    ``mutationWithoutValue("simulationPause")``) must fail on both APIs with
    the contract's exact error, publishing nothing."""
    query = "mutation MutationWithoutValue { simulationPause }"
    thrs_api = post(THRS_API_URL, query)
    mqtt_graphql = post(MQTT_GRAPHQL_URL, query)
    assert "errors" in thrs_api and "errors" in mqtt_graphql, (thrs_api, mqtt_graphql)
    assert (
        thrs_api["errors"][0]["message"]
        == mqtt_graphql["errors"][0]["message"]
        == contract.PAUSE.precondition_error
    )
    # Strawberry nulls the whole `data` on a mutation error where async-graphql
    # nulls the (nullable Void) field; the UI only looks at `error`.
    assert (thrs_api.get("data") or {}).get("simulationPause") is None
    assert (mqtt_graphql.get("data") or {}).get("simulationPause") is None


def test_simulation_play_out_of_range_rejected_on_both() -> None:
    """``simulationPlay(playbackRate: 100)`` violates the message model's bound
    (0.25..10) and must be rejected by both without publishing."""
    query = "mutation MutationWithValue($value: Float) { simulationPlay(playbackRate: $value) }"
    thrs_api = post(THRS_API_URL, query, {"value": 100.0})
    mqtt_graphql = post(MQTT_GRAPHQL_URL, query, {"value": 100.0})
    assert "errors" in thrs_api, thrs_api
    assert "errors" in mqtt_graphql, mqtt_graphql
    assert (thrs_api.get("data") or {}).get("simulationPlay") is None
    assert (mqtt_graphql.get("data") or {}).get("simulationPlay") is None
