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

Requires the docker stack (vernemq, thrs-api, mqtt-graphql). mqtt-graphql must
run with ``COMPUTED_MODE=recompute`` for the sensorValues sections to be
complete (thrs-api computes those fields itself; in relay mode they are only
present when the control loop publishes them).
"""

from __future__ import annotations

import asyncio
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest
from aiomqtt import Client as MqttClient
from pydantic import ValidationError

from tests.graphql.stack_config import mqtt_graphql_config, thrs_api_config
from thrs.control.switching import SwitchingControlMode
from thrs.graphql.simulation import io_mapping
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.wire_context import AMCS_RECEIVE_CONTEXT
from thrs.orchestration.comms import PartialMqttMapping, device_module_prefix
from thrs.runtime.messages import SimulationStatusMessage
from thrs.spec.asyncapi import all_module_descriptions

THRS_API_URL = "http://localhost:5102/graphql"
MQTT_GRAPHQL_URL = "http://localhost:5103/graphql"
MQTT_HOST = "localhost"
MQTT_PORT = 1883

# The two services read different prefixes in the dev stack (thrs-api's env vs
# the spec's baked-in defaults); seed both so both see the same state.
_CONFIGS = (thrs_api_config(), mqtt_graphql_config())
DEVICES_PREFIXES = tuple(c.mqtt_devices_topic_prefix for c in _CONFIGS)
CONTROLLER_PREFIXES = tuple(c.mqtt_controller_topic_prefix for c in _CONFIGS)
SIMULATOR_PREFIXES = tuple(c.mqtt_simulator_topic_prefix for c in _CONFIGS)

# The simulation whose inputs/outputs are seeded (thrs-api resolves the union
# member by which model validates; the UI selects `... on <X>SimulationInputsType`).
SEEDED_SIMULATION = "thrusters"

FLOAT_REL_TOL = 1e-9

# A few computed fields carry a read-time ``now()`` timestamp in thrs-api
# (``Stamped.stamp(0)`` for a heat-transfer device whose valve gate is off), so
# two reads of thrs-api *itself* differ there. Only a timestamp that is within
# this window of the wall clock on both sides, and that the two APIs place
# within ``NOW_JITTER_S`` of each other, is treated as equal; seeded timestamps
# still compare exactly (they are identical strings on both sides).
NOW_WINDOW_S = 60.0
NOW_JITTER_S = 2.0

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


# --- Seeding ------------------------------------------------------------------


def _seed_distinct_values(model: ThrsValues) -> None:
    """Give every float leaf a distinct in-bounds value (bool/enum leaves and
    out-of-bounds units keep their zero() value)."""
    counter = {"n": 0}

    def _visit(node: Any) -> None:
        if isinstance(node, Stamped):
            counter["n"] += 1
            try:
                node.value = 1.0 + counter["n"] * 0.01
            except (ValidationError, TypeError):
                pass
            return
        if isinstance(node, ThrsValues):
            for attr in type(node).model_fields:
                _visit(getattr(node, attr))

    _visit(model)


def _seeded(cls: type[ThrsValues]) -> ThrsValues:
    model = cls.zero()
    _seed_distinct_values(model)
    return model


def _control_mode_instance(cls: type[ThrsValues]) -> ThrsValues:
    """A populated control-mode model: every ``str`` field gets a marker
    value, nested groups recurse, a fieldless model is just empty."""
    values: dict[str, Any] = {}
    for name, fld in cls.model_fields.items():
        base = fld.annotation
        if isinstance(base, type) and issubclass(base, ThrsValues):
            values[name] = _control_mode_instance(base)
        else:
            values[name] = f"seeded-{name}"
    return cls(**values)


async def _seed_all(mqtt: MqttClient) -> None:
    modules = all_module_descriptions()
    for module, desc in modules.items():
        sensors = _seeded(desc.sensor_values_cls)
        actuated = _seeded(desc.control_values_cls)
        for prefix in DEVICES_PREFIXES:
            # A device publishes one payload per component carrying both its
            # sensor readings and the actuated (`CC_*`) control keys; thrs-api
            # reads sensorValues and controlValues off the same topics. Merge
            # the two serializations per topic so both sections complete.
            module_prefix = device_module_prefix(module)
            payloads: dict[str, dict[str, Any]] = {}
            sensor_mapping = PartialMqttMapping(type(sensors), prefix, module_prefix)
            for topic, payload in sensor_mapping.split_to_topics(sensors).items():
                payloads.setdefault(topic, {}).update(json.loads(payload))
            actuated_mapping = PartialMqttMapping(
                type(actuated), prefix, module_prefix, context=AMCS_RECEIVE_CONTEXT
            )
            for topic, payload in actuated_mapping.split_to_topics(actuated).items():
                payloads.setdefault(topic, {}).update(json.loads(payload))
            for topic, payload in payloads.items():
                await mqtt.publish(topic, payload=json.dumps(payload), retain=True)
        objects = {
            "manual-values": _seeded(desc.control_values_cls),
            "parameters": desc.parameters_cls(),
            "controller-state": _seeded(desc.controller_state_cls),
            "control-mode": SwitchingControlMode[desc.control_mode_cls](
                automatic_mode=_control_mode_instance(desc.control_mode_cls)
            ),
        }
        for kind, model in objects.items():
            payload = model.model_dump_json(by_alias=True)
            for prefix in CONTROLLER_PREFIXES:
                await mqtt.publish(
                    f"{prefix}/{module}/{kind}", payload=payload, retain=True
                )

    inputs_cls, outputs_cls = io_mapping[SEEDED_SIMULATION]
    status = SimulationStatusMessage(
        mode=SEEDED_SIMULATION,
        status="available",
        control_modules=[SEEDED_SIMULATION],
        simulation_time=datetime(2026, 1, 2, 3, 4, 5, 678901, tzinfo=UTC),
    )
    seeded_io = {
        "status": status,
        "simulation-inputs": _seeded(inputs_cls),
        "simulation-outputs": _seeded(outputs_cls),
    }
    for kind, model in seeded_io.items():
        payload = model.model_dump_json(by_alias=True)
        for prefix in SIMULATOR_PREFIXES:
            await mqtt.publish(f"{prefix}/{kind}", payload=payload, retain=True)


@pytest.fixture(scope="session", autouse=True)
def seeded_state() -> None:
    """Seed once per session; give both subscribers time to cache it."""

    async def _run() -> None:
        async with MqttClient(MQTT_HOST, MQTT_PORT) as mqtt:
            await _seed_all(mqtt)
            await asyncio.sleep(3.0)

    asyncio.run(_run())


# --- Helpers ------------------------------------------------------------------


def _post(
    url: str, query: str, variables: dict[str, Any] | None = None
) -> dict[str, Any]:
    response = httpx.post(
        url, json={"query": query, "variables": variables or {}}, timeout=30.0
    )
    response.raise_for_status()
    return response.json()


def _data(url: str, query: str) -> dict[str, Any]:
    body = _post(url, query)
    assert "errors" not in body, f"GraphQL errors from {url}: {body.get('errors')}"
    return body["data"]


def _diff(a: Any, b: Any, path: str = "$") -> list[str]:
    """Paths where the two documents differ (floats within tolerance)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(
                    f"{path}.{k}: only in {'thrs-api' if k in a else 'mqtt-graphql'}"
                )
            else:
                out += _diff(a[k], b[k], f"{path}.{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: list length {len(a)} != {len(b)}"]
        return [
            d for i, (x, y) in enumerate(zip(a, b)) for d in _diff(x, y, f"{path}[{i}]")
        ]
    if (
        isinstance(a, (int, float))
        and isinstance(b, (int, float))
        and not isinstance(a, bool)
        and not isinstance(b, bool)
    ):
        if math.isclose(float(a), float(b), rel_tol=FLOAT_REL_TOL, abs_tol=1e-12):
            return []
    if a == b:
        return []
    if isinstance(a, str) and isinstance(b, str) and _now_jitter(a, b):
        return []
    return [f"{path}: thrs-api={a!r} mqtt-graphql={b!r}"]


def _now_jitter(a: str, b: str) -> bool:
    try:
        ta, tb = datetime.fromisoformat(a), datetime.fromisoformat(b)
    except ValueError:
        return False
    now = datetime.now(UTC)
    within_window = all(
        abs((now - t).total_seconds()) <= NOW_WINDOW_S for t in (ta, tb)
    )
    return within_window and abs((ta - tb).total_seconds()) <= NOW_JITTER_S


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
    thrs_api = _data(THRS_API_URL, query)
    mqtt_graphql = _data(MQTT_GRAPHQL_URL, query)
    diffs = _diff(thrs_api, mqtt_graphql)
    assert not diffs, f"{document}: {len(diffs)} difference(s):\n" + "\n".join(
        diffs[:60]
    )


def test_query_all_is_non_trivial() -> None:
    """Guard against a vacuous pass: the seeded state must actually surface
    (every module's sections non-null, simulation inputs typed)."""
    data = _data(MQTT_GRAPHQL_URL, ui_query_all())
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
    body = _data(
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
    body = _data(
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
    thrs-api's exact error, publishing nothing."""
    query = "mutation MutationWithoutValue { simulationPause }"
    thrs_api = _post(THRS_API_URL, query)
    mqtt_graphql = _post(MQTT_GRAPHQL_URL, query)
    assert "errors" in thrs_api and "errors" in mqtt_graphql, (thrs_api, mqtt_graphql)
    assert (
        thrs_api["errors"][0]["message"]
        == mqtt_graphql["errors"][0]["message"]
        == ("Can only pause a running simulation")
    )
    # Strawberry nulls the whole `data` on a mutation error where async-graphql
    # nulls the (nullable Void) field; the UI only looks at `error`.
    assert (thrs_api.get("data") or {}).get("simulationPause") is None
    assert (mqtt_graphql.get("data") or {}).get("simulationPause") is None


def test_simulation_play_out_of_range_rejected_on_both() -> None:
    """``simulationPlay(playbackRate: 100)`` violates the message model's bound
    (0.25..10) and must be rejected by both without publishing."""
    query = "mutation MutationWithValue($value: Float) { simulationPlay(playbackRate: $value) }"
    thrs_api = _post(THRS_API_URL, query, {"value": 100.0})
    mqtt_graphql = _post(MQTT_GRAPHQL_URL, query, {"value": 100.0})
    assert "errors" in thrs_api, thrs_api
    assert "errors" in mqtt_graphql, mqtt_graphql
    assert (thrs_api.get("data") or {}).get("simulationPlay") is None
    assert (mqtt_graphql.get("data") or {}).get("simulationPlay") is None
