"""Every mutation, one by one: send it to the API and watch MQTT.

The write half of the thrs-api (5102) -> zero-mqtt-graphql (5103) migration is
"a GraphQL mutation becomes an MQTT publish". This suite drives *each* mutation
the specs declare -- every parameter of every module, every manual-control
component, every automation-mode switch, every simulation input component and
every simulation directive -- against **both** APIs and asserts, per element:

* exactly one publish appears on the mutation's set topic, and nothing else is
  published (no stray topics, no extra keys);
* that publish is the whole object the API held, with *only* the mutated field
  changed to the value we asked for (the expectation is built with THRS's own
  pydantic models, never typed by hand);
* the GraphQL response reflects the new value;
* after the controller "echoes" the publish back onto the state topic (this
  suite plays the controller: no control loop runs in the test stack) a read
  of the affected section on both APIs shows the new value (read-after-write);
* thrs-api and mqtt-graphql agree with each other on all of the above;
* out-of-range values (per-field bounds) and directive preconditions are
  rejected by both **without** publishing anything.

Unlike ``test_cross_api_mutation_parity.py``, which sets each parameter to its
own default (proving the mechanism byte-for-byte), this suite mutates to a
*different* value -- chosen by asking the parameters model itself which nearby
value it accepts, so cross-field invariants (thrs-api's ``model_validator``s)
hold on both sides -- and so proves the field actually changes.

Both services read different prefixes in the dev stack (see ``stack_config``):
each API is seeded, echoed and captured on its own prefix; the same spec
builders produce the topics for both, so no topic is hand-typed either.

Run from ``zero-thrs-control/`` with the stack up (vernemq, postgres, thrs-api,
mqtt-graphql; no thrs-control loop)::

    uv run pytest tests/graphql/test_mutation_mqtt_effects.py
"""

from __future__ import annotations

import asyncio
import json
import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import pytest
from aiomqtt import Client as MqttClient
from pydantic import TypeAdapter, ValidationError

from tests.graphql.parity import diff, graphql_literal, post, query_data, recent
from tests.graphql.resolved import ResolvedSpec, section_of
from tests.graphql.seeding import control_mode_instance, seeded
from tests.graphql.stack_config import (
    APIS,
    MQTT_GRAPHQL,
    MQTT_HOST,
    MQTT_PORT,
    THRS_API,
    URLS,
    mqtt_graphql_config,
    thrs_api_config,
)
from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import Stamped, ThrsValues
from thrs.runtime.descriptions.simulation import simulation_io_classes
from thrs.runtime.messages import SimulationStatusMessage
from thrs.spec import contract
from thrs.spec.asyncapi import all_module_descriptions
from thrs.spec.extension import component_class
from thrs.spec.naming import field_name

pytestmark = pytest.mark.migration

_THRS_CFG = thrs_api_config()
_MQTT_CFG = mqtt_graphql_config()
CONTROLLER_PREFIX = {
    THRS_API: _THRS_CFG.mqtt_controller_topic_prefix,
    MQTT_GRAPHQL: _MQTT_CFG.mqtt_controller_topic_prefix,
}
SIMULATOR_PREFIX = {
    THRS_API: _THRS_CFG.mqtt_simulator_topic_prefix,
    MQTT_GRAPHQL: _MQTT_CFG.mqtt_simulator_topic_prefix,
}

# Seconds after seeding before the mutation is sent (both services must have
# ingested the retained state), and after the response before the capture ends.
SEED_SETTLE_S = 0.8
POST_SETTLE_S = 0.4
# A restamped leaf (control/simulation input) carries the API's own now(); it
# must be within this window of the test's clock.
NOW_WINDOW_S = 30.0
FLOAT_REL_TOL = 1e-9


# --- Contract-derived case model -----------------------------------------------


@dataclass(frozen=True)
class Api:
    """One API under test with the contract generated for *its* prefixes."""

    name: str
    url: str
    contract: ResolvedSpec

    @property
    def members(self) -> dict[str, dict[str, Any]]:
        return self.contract.members

    @property
    def simulation(self) -> dict[str, Any]:
        return self.contract.lifecycle


API_SPECS = {
    THRS_API: Api(THRS_API, URLS[THRS_API], ResolvedSpec(_THRS_CFG)),
    MQTT_GRAPHQL: Api(MQTT_GRAPHQL, URLS[MQTT_GRAPHQL], ResolvedSpec(_MQTT_CFG)),
}
MODULES = all_module_descriptions()
SIM_MODE_BY_CAMEL = {field_name(mode): mode for mode in simulation_io_classes()}


def _topic(api: str, ref: dict[str, Any]) -> str:
    """The MQTT topic an operation reference resolves to in this API's document."""
    return API_SPECS[api].contract.topic(ref)


def _spec_mutation(api: str, module: str, gql_name: str) -> dict[str, Any]:
    for m in API_SPECS[api].members[module]["mutations"]:
        if m["gql"] == gql_name:
            return m
    raise KeyError(f"{api}: {module} has no mutation {gql_name}")


def _spec_sim_mutation(api: str, sim: str, gql_name: str) -> dict[str, Any]:
    for s in API_SPECS[api].simulation["members"]:
        if s["name"] == sim:
            for m in s["mutations"]:
                if m["gql"] == gql_name:
                    return m
    raise KeyError(f"{api}: simulation {sim} has no mutation {gql_name}")


def _spec_directive(api: str, gql_name: str) -> dict[str, Any]:
    for d in API_SPECS[api].simulation["directives"]:
        if d["gql"] == gql_name:
            return d
    raise KeyError(f"{api}: no directive {gql_name}")


def _alias_to_name(cls: type[ThrsValues]) -> dict[str, str]:
    """by-alias wire key -> python field name (ThrsValues models always carry
    an alias generator, so every field has an alias)."""
    return {fld.alias or name: name for name, fld in cls.model_fields.items()}


def _now_ts() -> datetime:
    return datetime.now(UTC)


# --- Picking a value the models accept ----------------------------------------


def _parameter_candidates(default: Any) -> list[Any]:
    if isinstance(default, bool):
        return [not default]
    if isinstance(default, int):
        return [default + 1, default - 1, default + 2]
    if isinstance(default, float):
        return [
            default + 1.0,
            default - 1.0,
            default * 1.5,
            default / 2.0,
            default + 0.25,
            default - 0.25,
        ]
    if isinstance(default, (list, tuple)):
        return [
            [v + 0.1 for v in default],
            [v * 2.0 + 0.01 for v in default],
            [v / 2.0 for v in default],
        ]
    return []


def _pick_parameter_value(
    params_cls: type[ThrsValues], name: str
) -> tuple[Any, ThrsValues, bool]:
    """A value for parameter ``name`` that differs from its default *and* that
    the parameters model accepts on assignment (single-field bounds plus the
    module's cross-field ``model_validator``s run under validate_assignment,
    exactly as thrs-api applies them). Returns (value, modified model, changed)
    where ``changed`` is False when no nearby value is accepted and the default
    is used instead (mechanism-only case, like the byte-parity suite)."""
    base = params_cls()
    default = getattr(base, name)
    for candidate in _parameter_candidates(default):
        try:
            modified = base.model_copy()
            setattr(modified, name, candidate)
        except ValidationError:
            continue
        if getattr(modified, name) != default:
            return getattr(modified, name), modified, True
    return default, base.model_copy(), False


def _leaf_candidates(leaf: dict[str, Any], current: Any) -> list[Any]:
    if leaf.get("enumValues"):
        # Wire values (as the model stores them, use_enum_values) != current.
        return [
            int(w) if w.lstrip("-").isdigit() else w
            for w in sorted(leaf["enumValues"], key=lambda w: (len(w), w))
            if (int(w) if w.lstrip("-").isdigit() else w) != current
        ]
    if leaf["type"] == "Boolean":
        return [not bool(current)]
    if leaf["type"] == "Int":
        return [int(current or 0) + 1, int(current or 0) + 2]
    return [
        v
        for v in (0.5, 0.25, 0.75, 2.5, 10.0, 42.0, 0.1, 100.0, 1.0)
        if not (isinstance(current, (int, float)) and math.isclose(v, current))
    ]


def _pick_component_input(
    component_cls: type[ThrsValues], current: ThrsValues, leaves: list[dict[str, Any]]
) -> tuple[dict[str, Any], ThrsValues]:
    """For a control/simulation component: one accepted, changed value per
    input field (validated through the field's own ``Stamped[T]`` annotation),
    returned as {gql: value} plus the stamped component it must become."""
    by_gql = {field_name(n): n for n in component_cls.model_fields}
    args: dict[str, Any] = {}
    stamped: dict[str, Any] = {}
    now = _now_ts()
    for leaf in leaves:
        name = by_gql[leaf["gql"]]
        annotation = component_cls.model_fields[name].annotation
        current_value = getattr(current, name).value
        chosen = None
        for candidate in _leaf_candidates(leaf, current_value):
            try:
                TypeAdapter(annotation).validate_python(
                    {"Value": candidate, "TimeStamp": now}
                )
            except ValidationError:
                continue
            chosen = candidate
            break
        assert chosen is not None, (
            f"no accepted candidate for {component_cls.__name__}.{name}"
        )
        args[leaf["gql"]] = chosen
        stamped[name] = Stamped(value=chosen, timestamp=now)
    return args, component_cls(**stamped)


def _inputgraphql_literal(args: dict[str, Any], leaves: list[dict[str, Any]]) -> str:
    parts = []
    for leaf in leaves:
        v = args[leaf["gql"]]
        if leaf.get("enumValues"):
            v = leaf["enumValues"][str(v)]  # wire value -> member name
        parts.append(f"{leaf['gql']}: {graphql_literal(v)}")
    return "{" + ", ".join(parts) + "}"


def _expected_leaf_values(
    args: dict[str, Any], leaves: list[dict[str, Any]]
) -> dict[str, Any]:
    """What the GraphQL response must show per leaf (enum -> member name)."""
    return {
        leaf["gql"]: (
            leaf["enumValues"][str(args[leaf["gql"]])]
            if leaf.get("enumValues")
            else args[leaf["gql"]]
        )
        for leaf in leaves
    }


def _selectable_leaves(
    section: dict[str, Any],
    component_gql_field: str,
    input_fields: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """The input leaves that can also be *selected* on the mutation's return
    type: thrs-api serves some components under a base type (a
    PropulsionDrive/Converter is a ``SimulationHeatSourceType`` with only
    ``heatFlow``), so the read section's leaves for the component - the same
    ones the spec's section builder emits - bound the response selection."""
    for f in section["fields"]:
        if f["gql"] == component_gql_field:
            served = {leaf["gql"] for leaf in f.get("leaves", [])}
            return [leaf for leaf in input_fields if leaf["gql"] in served]
    raise KeyError(f"{component_gql_field} not in section {section.get('typeName')}")


def _input_type_definitions() -> dict[str, list[list[dict[str, Any]]]]:
    """inputTypeName -> the distinct field shapes declared under that name, in
    thrs-api's registration order (module control mutations, then simulation
    input mutations). thrs-api names an input type after the component's
    Python class, and two different components can share a class name."""
    shapes: dict[str, list[list[dict[str, Any]]]] = {}
    declared: list[dict[str, Any]] = [
        m
        for module in sorted(MODULES)
        for m in API_SPECS[MQTT_GRAPHQL].members[module]["mutations"]
        if m["kind"] == "setComponent"
    ] + [
        m for s in API_SPECS[MQTT_GRAPHQL].simulation["members"] for m in s["mutations"]
    ]
    for m in declared:
        seen = shapes.setdefault(m["inputTypeName"], [])
        if m["inputFields"] not in seen:
            seen.append(m["inputFields"])
    return shapes


def _loses_input_type_collision(m: dict[str, Any]) -> bool:
    """True when this mutation's declared input shape is not the one the
    schema serves under its input type name (an earlier, differently shaped
    definition won)."""
    return _input_type_definitions()[m["inputTypeName"]][0] != m["inputFields"]


def _generic_inputgraphql_literal(input_fields: list[dict[str, Any]]) -> str:
    """A syntactically valid input literal for any field shape."""
    parts = []
    for leaf in input_fields:
        if leaf.get("enumValues"):
            v = min(leaf["enumValues"].values())
        elif leaf["type"] == "Boolean":
            v = True
        elif leaf["type"] == "Int":
            v = 1
        else:
            v = 0.5
        parts.append(f"{leaf['gql']}: {graphql_literal(v)}")
    return "{" + ", ".join(parts) + "}"


def _restamped_keys(spec: dict[str, Any]) -> set[str]:
    """Top-level keys whose timestamps the API stamps itself: the mutated
    component and every derived field that mirrors it (see the spec's
    ``derived``)."""
    return {spec["key"]} | {d["key"] for d in spec.get("derived") or []}


# --- MQTT harness -------------------------------------------------------------


@dataclass
class Capture:
    """Everything published (non-retained, not by us) while a mutation ran."""

    published: dict[str, list[Any]] = field(default_factory=dict)
    response: dict[str, Any] = field(default_factory=dict)

    def only(self, topic: str) -> Any:
        assert topic in self.published, (
            f"nothing published on {topic!r}; saw {sorted(self.published)!r}"
        )
        assert len(self.published[topic]) == 1, (
            f"{len(self.published[topic])} publishes on {topic!r}, expected 1"
        )
        return self.published[topic][0]

    def none(self) -> None:
        assert not self.published, f"unexpected publishes: {self.published!r}"


Echo = Callable[[Any], tuple[str, str] | None]


async def _run(
    url: str,
    query: str,
    seeds: dict[str, str],
    echo: dict[str, Echo] | None = None,
    variables: dict[str, Any] | None = None,
) -> Capture:
    """Seed retained state, POST the mutation, capture what it publishes. An
    ``echo`` maps a set topic to a function producing (state topic, payload)
    to publish retained the moment a publish on that set topic is seen: the
    controller's acknowledgement, which the API's echo-wait needs."""
    echo = echo or {}
    own_topics: set[str] = set(seeds)
    capture = Capture()
    async with MqttClient(MQTT_HOST, MQTT_PORT) as client:
        for topic, payload in seeds.items():
            await client.publish(topic, payload=payload, retain=True)
        await client.subscribe("#")

        async def _drain() -> None:
            async for msg in client.messages:
                topic = str(msg.topic)
                if msg.retain or topic in own_topics:
                    continue
                raw = msg.payload.decode()
                try:
                    value = json.loads(raw)
                except ValueError:
                    value = raw
                capture.published.setdefault(topic, []).append(value)
                if topic in echo:
                    reply = echo[topic](value)
                    if reply is not None:
                        state_topic, state_payload = reply
                        own_topics.add(state_topic)
                        await client.publish(
                            state_topic, payload=state_payload, retain=True
                        )

        task = asyncio.create_task(_drain())
        await asyncio.sleep(SEED_SETTLE_S)
        response = await asyncio.to_thread(post, url, query, variables)
        capture.response = response
        await asyncio.sleep(POST_SETTLE_S)
        task.cancel()
    return capture


def _dump(model: ThrsValues) -> dict[str, Any]:
    return json.loads(model.model_dump_json(by_alias=True))


# --- Comparing payloads --------------------------------------------------------


def recent_(ts: Any) -> bool:
    return recent(ts, NOW_WINDOW_S)


def diff_(
    a: Any, b: Any, path: str = "$", *, restamped: set[str] | None = None
) -> list[str]:
    """Paths where two JSON documents differ (see ``parity.diff``); under
    ``restamped`` a ``TimeStamp`` only has to be recent on both sides."""
    return diff(
        a,
        b,
        path,
        labels=("actual", "expected"),
        now_window_s=NOW_WINDOW_S,
        restamped=restamped,
    )


def _assert_same(
    label: str, actual: Any, expected: Any, *, restamped: set[str] | None = None
) -> None:
    diffs = diff_(actual, expected, restamped=restamped)
    assert not diffs, f"{label}: {len(diffs)} difference(s):\n  " + "\n  ".join(
        diffs[:40]
    )


def _value_at(data: Any, *keys: str) -> Any:
    for k in keys:
        assert isinstance(data, dict) and k in data, f"missing {k!r} in {data!r}"
        data = data[k]
    return data


# --- Case enumeration ------------------------------------------------------------


def _parameter_ids() -> list[tuple[str, str]]:
    return [
        (module, m["gql"])
        for module in sorted(MODULES)
        for m in API_SPECS[MQTT_GRAPHQL].members[module]["mutations"]
        if m["kind"] == "setField"
    ]


def _bounded_parameter_ids() -> list[tuple[str, str, str]]:
    return [
        (module, name, side)
        for module, name in _parameter_ids()
        for side in ("min", "exclusiveMin", "max", "exclusiveMax")
        if side in (_spec_mutation(MQTT_GRAPHQL, module, name).get("bounds") or {})
    ]


def _control_ids() -> list[tuple[str, str]]:
    return [
        (module, m["gql"])
        for module in sorted(MODULES)
        for m in API_SPECS[MQTT_GRAPHQL].members[module]["mutations"]
        if m["kind"] == "setComponent"
    ]


def _automation_ids() -> list[tuple[str, bool]]:
    return [
        (module, automatic) for module in sorted(MODULES) for automatic in (True, False)
    ]


def _simulation_ids() -> list[tuple[str, str]]:
    """Simulation input mutations whose input type the schema really serves
    (see ``_colliding_simulation_ids`` for the rest)."""
    return [
        (s["name"], m["gql"])
        for s in API_SPECS[MQTT_GRAPHQL].simulation["members"]
        for m in s["mutations"]
        if not _loses_input_type_collision(m)
    ]


def _colliding_simulation_ids() -> list[tuple[str, str]]:
    """Simulation input mutations whose input type name is already taken by a
    differently shaped control input (thrs-api: ``AdsorptionChillerInputType``
    is the 12-field control chiller, so ``{sim}SimulationSetAdsorptionChiller``
    can never be given its own one-field shape)."""
    return [
        (s["name"], m["gql"])
        for s in API_SPECS[MQTT_GRAPHQL].simulation["members"]
        for m in s["mutations"]
        if _loses_input_type_collision(m)
    ]


def _directive_specs() -> dict[str, Any]:
    """gql -> thrs-api's SimulationDirective (message class + guards)."""
    by_topic = {d.message.subscribe_topic(): d for d in contract.SIMULATION_DIRECTIVES}
    return {
        d["gql"]: by_topic[_topic(MQTT_GRAPHQL, d["target"]).rsplit("/", 1)[1]]
        for d in API_SPECS[MQTT_GRAPHQL].simulation["directives"]
    }


DIRECTIVES = _directive_specs()


def _directive_ids() -> list[tuple[str, str]]:
    """Every directive from every status it is allowed from (+ a play with an
    explicit rate)."""
    return [
        (name, status) for name, d in DIRECTIVES.items() for status in d.allowed_from
    ]


STATUSES = ("available", "running", "stepping")


def _directive_rejections() -> list[tuple[str, str]]:
    return [
        (name, status)
        for name, d in DIRECTIVES.items()
        for status in STATUSES
        if status not in d.allowed_from
    ]


# --- Tests: parameters -------------------------------------------------------------


@pytest.mark.parametrize(("module", "name"), _parameter_ids(), ids=lambda x: x)
def test_parameter_mutation_publishes_changed_object(module: str, name: str) -> None:
    """``{module}ParameterSet{Field}(value)`` on both APIs: exactly one publish
    on ``.../parameters/set`` equal to the seeded parameters object with only
    that field changed; the response returns the object with the new value;
    after the controller echo, ``modules.<module>.parameters.<field>`` reads
    the new value on both."""
    desc = MODULES[module]
    params_cls = desc.parameters_cls
    spec = _spec_mutation(MQTT_GRAPHQL, module, name)
    py_name = _alias_to_name(params_cls)[spec["key"]]
    value, modified, changed = _pick_parameter_value(params_cls, py_name)
    seed = _dump(params_cls())
    expected = _dump(modified)
    if changed:
        assert seed[spec["key"]] != expected[spec["key"]]
    gql_field = next(
        f["gql"]
        for f in section_of(API_SPECS[MQTT_GRAPHQL].members[module], "parameters")[
            "fields"
        ]
        if f["key"] == spec["key"]
    )
    is_list = spec["argType"].startswith("[")
    query = f"mutation {{ {name}({spec['argName']}: {graphql_literal(value)}) {{ {gql_field} }} }}"

    problems: list[str] = []
    for api in APIS:
        s = _spec_mutation(api, module, name)
        state, target = _topic(api, s["state"]), _topic(api, s["target"])
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={state: json.dumps(seed)},
                echo={target: lambda p, t=state: (t, json.dumps(p))},
            )
        )
        errors = cap.response.get("errors")
        if api == THRS_API and is_list and errors:
            # thrs-api quirk: a tuning tuple never compares equal to the list
            # argument in its echo check, so it reports a timeout after
            # publishing (see test_cross_api_mutation_parity).
            if errors[0]["message"] != contract.PARAMETERS_TIMEOUT_ERROR:
                problems.append(f"{api}: unexpected error {errors}")
        elif errors:
            problems.append(f"{api}: mutation errored: {errors}")
        else:
            got = _value_at(cap.response, "data", name, gql_field)
            if diff_(got, expected[spec["key"]]):
                problems.append(
                    f"{api}: response {gql_field}={got!r}, expected {expected[spec['key']]!r}"
                )
        try:
            published = cap.only(_topic(api, s["target"]))
        except AssertionError as e:
            problems.append(f"{api}: {e}")
            continue
        stray = sorted(set(cap.published) - {_topic(api, s["target"])})
        if stray:
            problems.append(f"{api}: stray publishes on {stray}")
        diffs = diff_(published, expected)
        if diffs:
            problems.append(
                f"{api}: published payload differs:\n    " + "\n    ".join(diffs[:20])
            )
        # Read-after-write: the echoed state is what both APIs now serve.
        data = query_data(
            URLS[api],
            f"{{ modules {{ {module} {{ parameters {{ {gql_field} }} }} }} }}",
        )
        read = _value_at(data, "modules", module, "parameters", gql_field)
        if diff_(read, expected[spec["key"]]):
            problems.append(
                f"{api}: read-after-write {gql_field}={read!r}, expected {expected[spec['key']]!r}"
            )
    assert not problems, (
        f"{module}.{name} (value={value!r}, changed={changed}):\n" + "\n".join(problems)
    )


@pytest.mark.parametrize(
    ("module", "name", "side"), _bounded_parameter_ids(), ids=lambda x: x
)
def test_parameter_out_of_bounds_rejected_without_publish(
    module: str, name: str, side: str
) -> None:
    """A value just past each declared bound is rejected by both APIs with an
    error, and nothing is published."""
    spec = _spec_mutation(MQTT_GRAPHQL, module, name)
    bound = spec["bounds"][side]
    value = {
        "min": bound - 1.0,
        "max": bound + 1.0,
        "exclusiveMin": bound,
        "exclusiveMax": bound,
    }[side]
    seed = _dump(MODULES[module].parameters_cls())
    query = f"mutation {{ {name}({spec['argName']}: {graphql_literal(value)}) {{ __typename }} }}"
    problems = []
    for api in APIS:
        s = _spec_mutation(api, module, name)
        cap = asyncio.run(
            _run(URLS[api], query, seeds={_topic(api, s["state"]): json.dumps(seed)})
        )
        if not cap.response.get("errors"):
            problems.append(
                f"{api}: accepted {value!r} ({side}={bound}): {cap.response}"
            )
        if (cap.response.get("data") or {}).get(name) is not None:
            problems.append(f"{api}: data.{name} not null: {cap.response.get('data')}")
        if cap.published:
            problems.append(f"{api}: published despite rejection: {cap.published}")
    assert not problems, (
        f"{module}.{name} {side}={bound} value={value!r}:\n" + "\n".join(problems)
    )


def _invariant_ids() -> list[tuple[str, str]]:
    return [
        (module, name)
        for module, name in _parameter_ids()
        if _spec_mutation(MQTT_GRAPHQL, module, name).get("invariants")
    ]


def _pick_invariant_violation(
    params_cls: type[ThrsValues], name: str, invariants: list[dict[str, Any]]
) -> tuple[Any, str] | None:
    """A value for parameter ``name`` the parameters model rejects on
    assignment through one of its cross-field invariants, with that
    invariant's error; None when no far-off value trips one (the field is
    not part of any)."""
    aliases = _alias_to_name(params_cls)
    errors = [
        i["error"] for i in invariants if name in (aliases[i["lhs"]], aliases[i["rhs"]])
    ]
    if not errors:
        return None
    base = params_cls()
    default = getattr(base, name)
    if isinstance(default, bool) or not isinstance(default, int | float):
        return None
    for delta in (1000.0, -1000.0, 100.0, -100.0, 10.0, -10.0, 1.0, -1.0):
        try:
            modified = base.model_copy()
            setattr(modified, name, default + delta)
        except ValidationError as e:
            message = str(e)
            hit = next((err for err in errors if err in message), None)
            if hit is not None:
                return default + delta, hit
    return None


@pytest.mark.parametrize(("module", "name"), _invariant_ids(), ids=lambda x: x)
def test_parameter_invariant_violation_rejected_without_publish(
    module: str, name: str
) -> None:
    """A value that breaks one of the parameters model's cross-field
    invariants is rejected by both APIs with that invariant's error, and
    nothing is published."""
    desc = MODULES[module]
    params_cls = desc.parameters_cls
    spec = _spec_mutation(MQTT_GRAPHQL, module, name)
    py_name = _alias_to_name(params_cls)[spec["key"]]
    violation = _pick_invariant_violation(params_cls, py_name, spec["invariants"])
    if violation is None:
        pytest.skip(f"{py_name} is not part of an invariant")
    value, error = violation
    seed = _dump(params_cls())
    query = f"mutation {{ {name}({spec['argName']}: {graphql_literal(value)}) {{ __typename }} }}"
    problems = []
    for api in APIS:
        s = _spec_mutation(api, module, name)
        cap = asyncio.run(
            _run(URLS[api], query, seeds={_topic(api, s["state"]): json.dumps(seed)})
        )
        errors = cap.response.get("errors") or []
        if not errors:
            problems.append(f"{api}: accepted {value!r}: {cap.response}")
        elif error not in errors[0]["message"]:
            problems.append(f"{api}: error {errors[0]['message']!r} lacks {error!r}")
        if (cap.response.get("data") or {}).get(name) is not None:
            problems.append(f"{api}: data.{name} not null: {cap.response.get('data')}")
        if cap.published:
            problems.append(f"{api}: published despite rejection: {cap.published}")
    assert not problems, f"{module}.{name} value={value!r}:\n" + "\n".join(problems)


def _unconfirmed_ids() -> list[tuple[str, str, str]]:
    """One mutation of every kind per module: the first parameter, the first
    control component and the automation switch."""
    cases = []
    for module in sorted(MODULES):
        for kind in ("setField", "setComponent", "setFlag"):
            first = next(
                (
                    m
                    for m in API_SPECS[MQTT_GRAPHQL].members[module]["mutations"]
                    if m["kind"] == kind and m.get("confirm")
                ),
                None,
            )
            if first is not None:
                cases.append((module, kind, first["gql"]))
    return cases


@pytest.mark.parametrize(
    ("module", "kind", "name"), _unconfirmed_ids(), ids=lambda x: x
)
def test_mutation_without_controller_echo_times_out_on_both(
    module: str, kind: str, name: str
) -> None:
    """Without a controller echoing the change, both APIs publish exactly once
    and then fail with the same timeout error after ``confirm.timeoutS``,
    returning no data."""
    desc = MODULES[module]
    spec = _spec_mutation(MQTT_GRAPHQL, module, name)
    if kind == "setField":
        py_name = _alias_to_name(desc.parameters_cls)[spec["key"]]
        value, _, _ = _pick_parameter_value(desc.parameters_cls, py_name)
        argument = graphql_literal(value)
        seed_model: ThrsValues = desc.parameters_cls()
        selection = " { __typename }"
    elif kind == "setComponent":
        cv_cls = desc.control_values_cls
        py_name = _alias_to_name(cv_cls)[spec["key"]]
        component_cls = component_class(cv_cls.model_fields[py_name].annotation)
        seed_model = seeded(cv_cls)
        args, _ = _pick_component_input(
            component_cls, getattr(seed_model, py_name), spec["inputFields"]
        )
        argument = _inputgraphql_literal(args, spec["inputFields"])
        selection = " { __typename }"
    else:
        argument = graphql_literal(True)
        seed_model = SwitchingControlMode[desc.control_mode_cls](automatic_mode=None)
        selection = ""
    query = f"mutation {{ {name}({spec['argName']}: {argument}){selection} }}"
    problems = []
    for api in APIS:
        s = _spec_mutation(api, module, name)
        state = _topic(api, s["confirm"].get("operation") or s["state"])
        started = time.monotonic()
        cap = asyncio.run(_run(URLS[api], query, seeds={state: _dump_json(seed_model)}))
        elapsed = time.monotonic() - started
        errors = cap.response.get("errors") or []
        if [e["message"] for e in errors] != [spec["confirm"]["timeoutError"]]:
            problems.append(f"{api}: errors {errors!r}")
        if (cap.response.get("data") or {}).get(name) is not None:
            problems.append(f"{api}: data.{name} not null: {cap.response.get('data')}")
        if elapsed < spec["confirm"]["timeoutS"]:
            problems.append(f"{api}: returned after {elapsed:.1f}s, before the timeout")
        try:
            cap.only(_topic(api, s["target"]))
        except AssertionError as e:
            problems.append(f"{api}: {e}")
    assert not problems, f"{module}.{name}:\n" + "\n".join(problems)


def _dump_json(model: ThrsValues) -> str:
    return model.model_dump_json(by_alias=True)


# --- Tests: manual control (manual-values) ----------------------------------------


@pytest.mark.parametrize(("module", "name"), _control_ids(), ids=lambda x: x)
def test_control_mutation_restamps_component(module: str, name: str) -> None:
    """``{module}ControlSet{Component}(value: {..})``: exactly one publish on
    ``.../manual-values/set`` equal to the seeded manual-values object with
    only that component replaced by the given leaves, each restamped with a
    recent timestamp; every other component byte-identical; the response
    shows the new leaf values; both APIs agree."""
    desc = MODULES[module]
    cv_cls = desc.control_values_cls
    spec = _spec_mutation(MQTT_GRAPHQL, module, name)
    py_name = _alias_to_name(cv_cls)[spec["key"]]
    component_cls = component_class(cv_cls.model_fields[py_name].annotation)
    seed_model = seeded(cv_cls)
    args, component = _pick_component_input(
        component_cls, getattr(seed_model, py_name), spec["inputFields"]
    )
    modified = seed_model.model_copy()
    setattr(modified, py_name, component)
    seed, expected = _dump(seed_model), _dump(modified)
    shown = _selectable_leaves(
        section_of(API_SPECS[MQTT_GRAPHQL].members[module], "controlValues"),
        spec["component"],
        spec["inputFields"],
    )
    leaves_sel = " ".join(f"{leaf['gql']} {{ value timestamp }}" for leaf in shown)
    query = (
        f"mutation {{ {name}({spec['argName']}: {_inputgraphql_literal(args, spec['inputFields'])}) "
        f"{{ {spec['component']} {{ {leaves_sel} }} }} }}"
    )
    want_leaves = _expected_leaf_values(args, shown)

    problems: list[str] = []
    payloads: dict[str, Any] = {}
    for api in APIS:
        s = _spec_mutation(api, module, name)
        state, target = _topic(api, s["state"]), _topic(api, s["target"])
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={state: json.dumps(seed)},
                echo={target: lambda p, t=state: (t, json.dumps(p))},
            )
        )
        if cap.response.get("errors"):
            problems.append(f"{api}: mutation errored: {cap.response['errors']}")
        else:
            comp = _value_at(cap.response, "data", name, spec["component"])
            for arg, want in want_leaves.items():
                got = comp.get(arg) or {}
                if diff_(got.get("value"), want):
                    problems.append(
                        f"{api}: response {arg}.value={got.get('value')!r}, expected {want!r}"
                    )
                if not recent_(got.get("timestamp")):
                    problems.append(
                        f"{api}: response {arg}.timestamp={got.get('timestamp')!r} not recent"
                    )
        try:
            published = cap.only(_topic(api, s["target"]))
        except AssertionError as e:
            problems.append(f"{api}: {e}")
            continue
        payloads[api] = published
        stray = sorted(set(cap.published) - {_topic(api, s["target"])})
        if stray:
            problems.append(f"{api}: stray publishes on {stray}")
        diffs = diff_(published, expected, restamped=_restamped_keys(spec))
        if diffs:
            problems.append(
                f"{api}: published payload differs:\n    " + "\n    ".join(diffs[:20])
            )
    if len(payloads) == 2:
        diffs = diff_(
            payloads[THRS_API], payloads[MQTT_GRAPHQL], restamped=_restamped_keys(spec)
        )
        if diffs:
            problems.append(
                "thrs-api vs mqtt-graphql payloads differ:\n    "
                + "\n    ".join(diffs[:20])
            )
    assert not problems, f"{module}.{name} (args={args!r}):\n" + "\n".join(problems)


# --- Tests: automation mode ----------------------------------------------------------


@pytest.mark.parametrize(("module", "automatic"), _automation_ids(), ids=str)
def test_automation_mode_publishes_mode(module: str, automatic: bool) -> None:
    """``{module}SetAutomationMode(automatic)``: exactly one publish of the
    ``AutomationMode`` object on ``.../automation-mode/set``; response is the
    boolean; after the controller echoes the resulting control-mode,
    ``controlMode.automatic`` reads back on both APIs."""
    desc = MODULES[module]
    expected = _dump(AutomationMode.for_automatic(automatic))
    spec = _spec_mutation(
        MQTT_GRAPHQL, module, f"{field_name(module)}SetAutomationMode"
    )
    query = (
        f"mutation {{ {spec['gql']}({spec['argName']}: {graphql_literal(automatic)}) }}"
    )
    control_mode = SwitchingControlMode[desc.control_mode_cls](
        automatic_mode=control_mode_instance(desc.control_mode_cls)
        if automatic
        else None
    )
    problems = []
    for api in APIS:
        s = _spec_mutation(api, module, spec["gql"])
        state = _topic(api, s["confirm"]["operation"])
        # Start from the opposite mode so the read-after-write proves a change.
        opposite = SwitchingControlMode[desc.control_mode_cls](
            automatic_mode=None
            if automatic
            else control_mode_instance(desc.control_mode_cls)
        )
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={state: opposite.model_dump_json(by_alias=True)},
                echo={
                    _topic(api, s["target"]): lambda _p, t=state: (
                        t,
                        control_mode.model_dump_json(by_alias=True),
                    )
                },
            )
        )
        if cap.response.get("errors"):
            problems.append(f"{api}: errored: {cap.response['errors']}")
        elif _value_at(cap.response, "data", spec["gql"]) is not automatic:
            problems.append(
                f"{api}: returned {cap.response['data']!r}, expected {automatic}"
            )
        try:
            published = cap.only(_topic(api, s["target"]))
        except AssertionError as e:
            problems.append(f"{api}: {e}")
            continue
        stray = sorted(set(cap.published) - {_topic(api, s["target"])})
        if stray:
            problems.append(f"{api}: stray publishes on {stray}")
        if diff_(published, expected):
            problems.append(f"{api}: published {published!r}, expected {expected!r}")
        data = query_data(
            URLS[api], f"{{ modules {{ {module} {{ controlMode {{ automatic }} }} }} }}"
        )
        read = _value_at(data, "modules", module, "controlMode")
        if read is None or read.get("automatic") is not automatic:
            problems.append(
                f"{api}: read-after-write controlMode={read!r}, expected automatic={automatic}"
            )
    assert not problems, f"{module} automatic={automatic}:\n" + "\n".join(problems)


# --- Tests: simulation inputs --------------------------------------------------------


def _seed_status(api: str, mode: str, status: str) -> tuple[str, str]:
    msg = SimulationStatusMessage(
        mode=mode,
        status=status,  # type: ignore[arg-type]
        control_modules=[mode],
        simulation_time=datetime(2026, 1, 2, 3, 4, 5, 678901, tzinfo=UTC),
    )
    return _topic(
        api, API_SPECS[api].simulation["status"]["operation"]
    ), msg.model_dump_json(by_alias=True)


@pytest.mark.parametrize(("sim", "name"), _simulation_ids(), ids=lambda x: x)
def test_simulation_input_mutation_restamps_component(sim: str, name: str) -> None:
    """``{sim}SimulationSet{Component}(value: {..})``: exactly one publish on
    the simulation-inputs set topic equal to the seeded inputs object of that
    simulation with only that component replaced (restamped); response shows
    the new leaves; after the echo ``simulation.inputs`` reads them back typed
    as that simulation on both APIs."""
    mode = SIM_MODE_BY_CAMEL[sim]
    inputs_cls, _ = simulation_io_classes()[mode]
    spec = _spec_sim_mutation(MQTT_GRAPHQL, sim, name)
    sim_spec = next(
        s for s in API_SPECS[MQTT_GRAPHQL].simulation["members"] if s["name"] == sim
    )
    py_name = _alias_to_name(inputs_cls)[spec["key"]]
    component_cls = component_class(inputs_cls.model_fields[py_name].annotation)
    seed_model = seeded(inputs_cls)
    args, component = _pick_component_input(
        component_cls, getattr(seed_model, py_name), spec["inputFields"]
    )
    modified = seed_model.model_copy()
    setattr(modified, py_name, component)
    seed, expected = _dump(seed_model), _dump(modified)
    shown = _selectable_leaves(
        section_of(sim_spec, "inputs"), spec["component"], spec["inputFields"]
    )
    leaves_sel = " ".join(f"{leaf['gql']} {{ value timestamp }}" for leaf in shown)
    query = (
        f"mutation {{ {name}({spec['argName']}: {_inputgraphql_literal(args, spec['inputFields'])}) "
        f"{{ {spec['component']} {{ {leaves_sel} }} }} }}"
    )
    want_leaves = _expected_leaf_values(args, shown)
    read_query = (
        f"{{ simulation {{ inputs {{ __typename ... on {section_of(sim_spec, 'inputs')['typeName']} "
        f"{{ {spec['component']} {{ {leaves_sel} }} }} }} }} }}"
    )

    problems: list[str] = []
    payloads: dict[str, Any] = {}
    for api in APIS:
        s = _spec_sim_mutation(api, sim, name)
        status_topic, status_payload = _seed_status(api, mode, "available")
        state, target = _topic(api, s["state"]), _topic(api, s["target"])
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={state: json.dumps(seed), status_topic: status_payload},
                echo={target: lambda p, t=state: (t, json.dumps(p))},
            )
        )
        if cap.response.get("errors"):
            problems.append(f"{api}: mutation errored: {cap.response['errors']}")
        else:
            comp = _value_at(cap.response, "data", name, spec["component"])
            for arg, want in want_leaves.items():
                got = comp.get(arg) or {}
                if diff_(got.get("value"), want):
                    problems.append(
                        f"{api}: response {arg}.value={got.get('value')!r}, expected {want!r}"
                    )
                if not recent_(got.get("timestamp")):
                    problems.append(
                        f"{api}: response {arg}.timestamp={got.get('timestamp')!r} not recent"
                    )
        try:
            published = cap.only(_topic(api, s["target"]))
        except AssertionError as e:
            problems.append(f"{api}: {e}")
            continue
        payloads[api] = published
        stray = sorted(set(cap.published) - {_topic(api, s["target"])})
        if stray:
            problems.append(f"{api}: stray publishes on {stray}")
        diffs = diff_(published, expected, restamped=_restamped_keys(spec))
        if diffs:
            problems.append(
                f"{api}: published payload differs:\n    " + "\n    ".join(diffs[:20])
            )
        data = query_data(URLS[api], read_query)
        inputs = _value_at(data, "simulation", "inputs")
        if (
            inputs is None
            or inputs.get("__typename") != section_of(sim_spec, "inputs")["typeName"]
        ):
            problems.append(
                f"{api}: read-after-write inputs={inputs!r}, expected {section_of(sim_spec, 'inputs')['typeName']}"
            )
        else:
            comp = inputs.get(spec["component"]) or {}
            for arg, want in want_leaves.items():
                got = (comp.get(arg) or {}).get("value")
                if diff_(got, want):
                    problems.append(
                        f"{api}: read-after-write {arg}.value={got!r}, expected {want!r}"
                    )
    if len(payloads) == 2:
        diffs = diff_(
            payloads[THRS_API], payloads[MQTT_GRAPHQL], restamped=_restamped_keys(spec)
        )
        if diffs:
            problems.append(
                "thrs-api vs mqtt-graphql payloads differ:\n    "
                + "\n    ".join(diffs[:20])
            )
    assert not problems, f"{sim}.{name} (args={args!r}):\n" + "\n".join(problems)


@pytest.mark.parametrize(("sim", "name"), _colliding_simulation_ids(), ids=lambda x: x)
def test_colliding_input_type_simulation_mutation_rejected(sim: str, name: str) -> None:
    """A simulation input mutation whose input type name collides with a
    differently shaped control input is unusable on thrs-api: its own shape
    fails GraphQL validation (the served type has other fields) and the served
    shape fails the simulation model's validation. mqtt-graphql must mirror
    both outcomes: an error and no publish, never a spurious inputs object."""
    mode = SIM_MODE_BY_CAMEL[sim]
    inputs_cls, _ = simulation_io_classes()[mode]
    spec = _spec_sim_mutation(MQTT_GRAPHQL, sim, name)
    served_shape = _input_type_definitions()[spec["inputTypeName"]][0]
    seed = _dump(seeded(inputs_cls))
    queries = {
        "own shape": f"mutation {{ {name}({spec['argName']}: "
        f"{_generic_inputgraphql_literal(spec['inputFields'])}) {{ __typename }} }}",
        "served shape": f"mutation {{ {name}({spec['argName']}: "
        f"{_generic_inputgraphql_literal(served_shape)}) {{ __typename }} }}",
    }
    problems = []
    for label, query in queries.items():
        for api in APIS:
            s = _spec_sim_mutation(api, sim, name)
            status_topic, status_payload = _seed_status(api, mode, "available")
            cap = asyncio.run(
                _run(
                    URLS[api],
                    query,
                    seeds={
                        _topic(api, s["state"]): json.dumps(seed),
                        status_topic: status_payload,
                    },
                )
            )
            if not cap.response.get("errors"):
                problems.append(f"{api} ({label}): accepted: {cap.response}")
            if (cap.response.get("data") or {}).get(name) is not None:
                problems.append(f"{api} ({label}): data.{name} not null")
            if cap.published:
                problems.append(f"{api} ({label}): published: {cap.published}")
    assert not problems, f"{sim}.{name}:\n" + "\n".join(problems)


# --- Tests: simulation directives ------------------------------------------------


def _directivequery_data(
    name: str, spec: dict[str, Any], arg: float | None
) -> tuple[str, dict[str, Any]]:
    if arg is None or spec.get("argName") is None:
        return f"mutation {{ {name} }}", {}
    return f"mutation ($v: Float!) {{ {name}({spec['argName']}: $v) }}", {"v": arg}


def _directive_arg(name: str, spec: dict[str, Any]) -> float | None:
    """An explicit in-range argument for a directive that takes one."""
    if spec.get("argName") is None:
        return None
    bounds = spec.get("bounds") or {}
    lo = bounds.get("min", bounds.get("exclusiveMin", 0.0))
    hi = bounds.get("max", lo + 10.0)
    return round(lo + (hi - lo) * 0.3 + 0.01, 3)


@pytest.mark.parametrize(("name", "status"), _directive_ids(), ids=lambda x: x)
def test_directive_publishes_and_waits_for_status(name: str, status: str) -> None:
    """From every status a directive is allowed in: both APIs publish the
    directive message once (the model's by-alias JSON), then succeed once the
    simulator (played by this test) reports the expected status. Play is
    exercised with its default and with an explicit rate."""
    directive = DIRECTIVES[name]
    spec = _spec_directive(MQTT_GRAPHQL, name)
    variants: list[float | None] = [None]
    if spec.get("argName") is not None:
        variants = [_directive_arg(name, spec)] + (
            [None] if not spec.get("argRequired") else []
        )
    problems = []
    for arg in variants:
        message_kwargs = (
            {} if arg is None else {next(iter(directive.message.model_fields)): arg}
        )
        expected = _dump(directive.message(**message_kwargs))
        query, variables = _directivequery_data(name, spec, arg)
        for api in APIS:
            s = _spec_directive(api, name)
            status_topic, seed_payload = _seed_status(api, "thrusters", status)
            _, expect_payload = _seed_status(api, "thrusters", directive.expect_status)
            cap = asyncio.run(
                _run(
                    URLS[api],
                    query,
                    seeds={status_topic: seed_payload},
                    echo={
                        _topic(
                            api, s["target"]
                        ): lambda _p, t=status_topic, pl=expect_payload: (
                            t,
                            pl,
                        )
                    },
                    variables=variables,
                )
            )
            label = f"{api} arg={arg!r} from={status}"
            if cap.response.get("errors"):
                problems.append(f"{label}: errored: {cap.response['errors']}")
            try:
                published = cap.only(_topic(api, s["target"]))
            except AssertionError as e:
                problems.append(f"{label}: {e}")
                continue
            stray = sorted(set(cap.published) - {_topic(api, s["target"])})
            if stray:
                problems.append(f"{label}: stray publishes on {stray}")
            if diff_(published, expected):
                problems.append(
                    f"{label}: published {published!r}, expected {expected!r}"
                )
    assert not problems, f"{name} from {status}:\n" + "\n".join(problems)


@pytest.mark.parametrize(("name", "status"), _directive_rejections(), ids=lambda x: x)
def test_directive_precondition_rejects_without_publish(name: str, status: str) -> None:
    """From a status the directive is not allowed in, both APIs answer with
    thrs-api's exact precondition error and publish nothing."""
    directive = DIRECTIVES[name]
    spec = _spec_directive(MQTT_GRAPHQL, name)
    query, variables = _directivequery_data(name, spec, _directive_arg(name, spec))
    problems = []
    for api in APIS:
        status_topic, seed_payload = _seed_status(api, "thrusters", status)
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={status_topic: seed_payload},
                variables=variables,
            )
        )
        errors = cap.response.get("errors") or []
        if not errors or errors[0]["message"] != directive.precondition_error:
            problems.append(
                f"{api}: expected {directive.precondition_error!r}, got {cap.response!r}"
            )
        if (cap.response.get("data") or {}).get(name) is not None:
            problems.append(f"{api}: data.{name} not null")
        if cap.published:
            problems.append(f"{api}: published despite precondition: {cap.published}")
    assert not problems, f"{name} from {status}:\n" + "\n".join(problems)


def _directive_bound_cases() -> list[tuple[str, str]]:
    return [
        (name, side)
        for name in DIRECTIVES
        for side in ("min", "exclusiveMin", "max", "exclusiveMax")
        if side in (_spec_directive(MQTT_GRAPHQL, name).get("bounds") or {})
    ]


@pytest.mark.parametrize(("name", "side"), _directive_bound_cases(), ids=lambda x: x)
def test_directive_out_of_bounds_rejected_without_publish(name: str, side: str) -> None:
    """A directive argument past its message model's bound is rejected by both
    APIs without publishing (seeded from an allowed status, so only the bound
    can be the reason)."""
    directive = DIRECTIVES[name]
    spec = _spec_directive(MQTT_GRAPHQL, name)
    bound = spec["bounds"][side]
    value = {
        "min": bound - 1.0,
        "max": bound + 1.0,
        "exclusiveMin": bound,
        "exclusiveMax": bound,
    }[side]
    query, variables = _directivequery_data(name, spec, value)
    problems = []
    for api in APIS:
        status_topic, seed_payload = _seed_status(
            api, "thrusters", directive.allowed_from[0]
        )
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={status_topic: seed_payload},
                variables=variables,
            )
        )
        if not cap.response.get("errors"):
            problems.append(
                f"{api}: accepted {value!r} ({side}={bound}): {cap.response}"
            )
        if cap.published:
            problems.append(f"{api}: published despite rejection: {cap.published}")
    assert not problems, f"{name} {side}={bound} value={value!r}:\n" + "\n".join(
        problems
    )


# --- Test: the enumeration itself is complete -------------------------------------


def test_every_spec_mutation_is_covered() -> None:
    """Guard against a silent gap: every mutation kind the specs declare maps
    to one of the parametrized tests above, and the two APIs' specs list the
    same mutations (only prefixes differ)."""
    covered = {n for _, n in _parameter_ids()} | {n for _, n in _control_ids()}
    covered |= {f"{field_name(m)}SetAutomationMode" for m in MODULES}
    covered |= {n for _, n in _simulation_ids()} | set(DIRECTIVES)
    covered |= {n for _, n in _colliding_simulation_ids()}
    declared: set[str] = set()
    for api in APIS:
        for module, spec in API_SPECS[api].members.items():
            for m in spec["mutations"]:
                assert m["kind"] in ("setField", "setComponent", "setFlag"), (
                    module,
                    m,
                )
                declared.add(m["gql"])
        for s in API_SPECS[api].simulation["members"]:
            declared |= {m["gql"] for m in s["mutations"]}
        declared |= {d["gql"] for d in API_SPECS[api].simulation["directives"]}
    assert declared == covered, {
        "not covered": sorted(declared - covered),
        "not declared": sorted(covered - declared),
    }
    assert len(covered) >= 300, f"only {len(covered)} mutations enumerated"
