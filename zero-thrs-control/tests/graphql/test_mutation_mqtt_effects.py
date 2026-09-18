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
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import httpx
import pytest
from aiomqtt import Client as MqttClient
from pydantic import TypeAdapter, ValidationError
from strawberry.utils.str_converters import to_camel_case

from tests.graphql.stack_config import mqtt_graphql_config, thrs_api_config
from tests.graphql.test_cross_api_ui_parity import _control_mode_instance, _seeded
from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.graphql.base import SIMULATION_DIRECTIVE_RESOLVERS
from thrs.graphql.messaging import PARAMETERS_TIMEOUT_ERROR
from thrs.graphql.simulation import io_mapping
from thrs.input_output.base import Stamped, ThrsValues
from thrs.runtime.messages import SimulationStatusMessage
from thrs.spec.asyncapi import (
    _bare_type,
    all_module_descriptions,
    build_module_mutations,
    build_simulation_view,
)

MQTT_HOST = "localhost"
MQTT_PORT = 1883

THRS_API = "thrs-api"
MQTT_GRAPHQL = "mqtt-graphql"
URLS = {
    THRS_API: "http://localhost:5102/graphql",
    MQTT_GRAPHQL: "http://localhost:5103/graphql",
}
APIS = (THRS_API, MQTT_GRAPHQL)

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


# --- Spec-derived case model -------------------------------------------------


@dataclass(frozen=True)
class Api:
    """One API under test with the spec generated for *its* prefixes."""

    name: str
    url: str
    module_mutations: dict[str, dict[str, Any]]
    simulation: dict[str, Any]


def _apis() -> dict[str, Api]:
    modules = sorted(all_module_descriptions())
    return {
        THRS_API: Api(
            THRS_API,
            URLS[THRS_API],
            {
                m: build_module_mutations(
                    m, controller_prefix=CONTROLLER_PREFIX[THRS_API]
                )
                for m in modules
            },
            build_simulation_view(simulator_prefix=SIMULATOR_PREFIX[THRS_API]),
        ),
        MQTT_GRAPHQL: Api(
            MQTT_GRAPHQL,
            URLS[MQTT_GRAPHQL],
            {
                m: build_module_mutations(
                    m, controller_prefix=CONTROLLER_PREFIX[MQTT_GRAPHQL]
                )
                for m in modules
            },
            build_simulation_view(simulator_prefix=SIMULATOR_PREFIX[MQTT_GRAPHQL]),
        ),
    }


API_SPECS = _apis()
MODULES = all_module_descriptions()
SIM_MODE_BY_CAMEL = {to_camel_case(mode): mode for mode in io_mapping}


def _spec_mutation(api: str, module: str, gql_name: str) -> dict[str, Any]:
    for m in API_SPECS[api].module_mutations[module]["mutations"]:
        if m["gqlName"] == gql_name:
            return m
    raise KeyError(f"{api}: {module} has no mutation {gql_name}")


def _spec_sim_mutation(api: str, sim: str, gql_name: str) -> dict[str, Any]:
    for s in API_SPECS[api].simulation["simulations"]:
        if s["name"] == sim:
            for m in s["mutations"]:
                if m["gqlName"] == gql_name:
                    return m
    raise KeyError(f"{api}: simulation {sim} has no mutation {gql_name}")


def _spec_directive(api: str, gql_name: str) -> dict[str, Any]:
    for d in API_SPECS[api].simulation["directives"]:
        if d["gqlName"] == gql_name:
            return d
    raise KeyError(f"{api}: no directive {gql_name}")


def _alias_to_name(cls: type[ThrsValues]) -> dict[str, str]:
    """by-alias wire key -> python field name (ThrsValues models always carry
    an alias generator, so every field has an alias)."""
    return {fld.alias or name: name for name, fld in cls.model_fields.items()}


def _now_ts() -> datetime:
    return datetime.now(UTC)


# --- Picking a value the models accept ----------------------------------------


def _literal(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_literal(v) for v in value) + "]"
    if isinstance(value, str):
        return value  # enum member name (unquoted GraphQL enum literal)
    return repr(value)


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
    returned as {argName: value} plus the stamped component it must become."""
    by_gql = {to_camel_case(n): n for n in component_cls.model_fields}
    args: dict[str, Any] = {}
    stamped: dict[str, Any] = {}
    now = _now_ts()
    for leaf in leaves:
        name = by_gql[leaf["argName"]]
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
        args[leaf["argName"]] = chosen
        stamped[name] = Stamped(value=chosen, timestamp=now)
    return args, component_cls(**stamped)


def _input_literal(args: dict[str, Any], leaves: list[dict[str, Any]]) -> str:
    parts = []
    for leaf in leaves:
        v = args[leaf["argName"]]
        if leaf.get("enumValues"):
            v = leaf["enumValues"][str(v)]  # wire value -> member name
        parts.append(f"{leaf['argName']}: {_literal(v)}")
    return "{" + ", ".join(parts) + "}"


def _expected_leaf_values(
    args: dict[str, Any], leaves: list[dict[str, Any]]
) -> dict[str, Any]:
    """What the GraphQL response must show per leaf (enum -> member name)."""
    return {
        leaf["argName"]: (
            leaf["enumValues"][str(args[leaf["argName"]])]
            if leaf.get("enumValues")
            else args[leaf["argName"]]
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
        if f["gqlField"] == component_gql_field:
            served = {leaf["gql"] for leaf in f.get("leaves", [])}
            return [leaf for leaf in input_fields if leaf["argName"] in served]
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
        for m in API_SPECS[MQTT_GRAPHQL].module_mutations[module]["mutations"]
        if m["kind"] == "control"
    ] + [
        m
        for s in API_SPECS[MQTT_GRAPHQL].simulation["simulations"]
        for m in s["mutations"]
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


def _generic_input_literal(input_fields: list[dict[str, Any]]) -> str:
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
        parts.append(f"{leaf['argName']}: {_literal(v)}")
    return "{" + ", ".join(parts) + "}"


def _restamped_keys(spec: dict[str, Any]) -> set[str]:
    """Top-level keys whose timestamps the API stamps itself: the mutated
    component and every derived field that mirrors it (see the spec's
    ``derived``)."""
    return {spec["payloadKey"]} | {d["key"] for d in spec.get("derived") or []}


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
        response = await asyncio.to_thread(_post, url, query, variables)
        capture.response = response
        await asyncio.sleep(POST_SETTLE_S)
        task.cancel()
    return capture


def _post(url: str, query: str, variables: dict[str, Any] | None) -> dict[str, Any]:
    r = httpx.post(
        url, json={"query": query, "variables": variables or {}}, timeout=20.0
    )
    r.raise_for_status()
    return r.json()


def _query(url: str, query: str) -> dict[str, Any]:
    body = _post(url, query, None)
    assert "errors" not in body, f"{url}: {body.get('errors')}"
    return body["data"]


def _dump(model: ThrsValues) -> dict[str, Any]:
    return json.loads(model.model_dump_json(by_alias=True))


# --- Comparing payloads --------------------------------------------------------


def _recent(ts: Any) -> bool:
    try:
        t = datetime.fromisoformat(str(ts))
    except ValueError:
        return False
    return abs((_now_ts() - t).total_seconds()) <= NOW_WINDOW_S


def _diff(
    a: Any, b: Any, path: str = "$", *, restamped: set[str] | None = None
) -> list[str]:
    """Paths where two JSON documents differ. Floats compare within tolerance.
    Under ``restamped`` (a top-level key whose component the API restamped with
    its own now()), a ``TimeStamp`` only has to be recent on both sides."""
    if isinstance(a, dict) and isinstance(b, dict):
        out: list[str] = []
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}.{k}: only in {'left' if k in a else 'right'}")
                continue
            if (
                k == "TimeStamp"
                and restamped
                and any(path.startswith(f"$.{r}") for r in restamped)
            ):
                if a[k] != b[k] and not (_recent(a[k]) and _recent(b[k])):
                    out.append(
                        f"{path}.{k}: not a recent timestamp ({a[k]!r} / {b[k]!r})"
                    )
                continue
            out += _diff(a[k], b[k], f"{path}.{k}", restamped=restamped)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [
            d
            for i, (x, y) in enumerate(zip(a, b, strict=True))
            for d in _diff(x, y, f"{path}[{i}]", restamped=restamped)
        ]
    if (
        isinstance(a, (int, float))
        and isinstance(b, (int, float))
        and not isinstance(a, bool)
        and not isinstance(b, bool)
        and math.isclose(float(a), float(b), rel_tol=FLOAT_REL_TOL, abs_tol=1e-12)
    ):
        return []
    if a == b:
        return []
    return [f"{path}: {a!r} != {b!r}"]


def _assert_same(
    label: str, actual: Any, expected: Any, *, restamped: set[str] | None = None
) -> None:
    diffs = _diff(actual, expected, restamped=restamped)
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
        (module, m["gqlName"])
        for module in sorted(MODULES)
        for m in API_SPECS[MQTT_GRAPHQL].module_mutations[module]["mutations"]
        if m["kind"] == "parameter"
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
        (module, m["gqlName"])
        for module in sorted(MODULES)
        for m in API_SPECS[MQTT_GRAPHQL].module_mutations[module]["mutations"]
        if m["kind"] == "control"
    ]


def _automation_ids() -> list[tuple[str, bool]]:
    return [
        (module, automatic) for module in sorted(MODULES) for automatic in (True, False)
    ]


def _simulation_ids() -> list[tuple[str, str]]:
    """Simulation input mutations whose input type the schema really serves
    (see ``_colliding_simulation_ids`` for the rest)."""
    return [
        (s["name"], m["gqlName"])
        for s in API_SPECS[MQTT_GRAPHQL].simulation["simulations"]
        for m in s["mutations"]
        if not _loses_input_type_collision(m)
    ]


def _colliding_simulation_ids() -> list[tuple[str, str]]:
    """Simulation input mutations whose input type name is already taken by a
    differently shaped control input (thrs-api: ``AdsorptionChillerInputType``
    is the 12-field control chiller, so ``{sim}SimulationSetAdsorptionChiller``
    can never be given its own one-field shape)."""
    return [
        (s["name"], m["gqlName"])
        for s in API_SPECS[MQTT_GRAPHQL].simulation["simulations"]
        for m in s["mutations"]
        if _loses_input_type_collision(m)
    ]


def _directive_specs() -> dict[str, Any]:
    """gqlName -> thrs-api's SimulationDirective (message class + guards)."""
    by_topic = {d.message.subscribe_topic(): d for d in SIMULATION_DIRECTIVE_RESOLVERS}
    return {
        d["gqlName"]: by_topic[d["topic"].rsplit("/", 1)[1]]
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
    py_name = _alias_to_name(params_cls)[spec["payloadKey"]]
    value, modified, changed = _pick_parameter_value(params_cls, py_name)
    seed = _dump(params_cls())
    expected = _dump(modified)
    if changed:
        assert seed[spec["payloadKey"]] != expected[spec["payloadKey"]]
    gql_field = next(
        f["gqlField"]
        for f in API_SPECS[MQTT_GRAPHQL].module_mutations[module]["parametersObject"][
            "fields"
        ]
        if f["key"] == spec["payloadKey"]
    )
    is_list = spec["argType"].startswith("[")
    query = (
        f"mutation {{ {name}({spec['argName']}: {_literal(value)}) {{ {gql_field} }} }}"
    )

    problems: list[str] = []
    for api in APIS:
        s = _spec_mutation(api, module, name)
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={s["stateTopic"]: json.dumps(seed)},
                echo={s["setTopic"]: lambda p, t=s["stateTopic"]: (t, json.dumps(p))},
            )
        )
        errors = cap.response.get("errors")
        if api == THRS_API and is_list and errors:
            # thrs-api quirk: a tuning tuple never compares equal to the list
            # argument in its echo check, so it reports a timeout after
            # publishing (see test_cross_api_mutation_parity).
            if errors[0]["message"] != PARAMETERS_TIMEOUT_ERROR:
                problems.append(f"{api}: unexpected error {errors}")
        elif errors:
            problems.append(f"{api}: mutation errored: {errors}")
        else:
            got = _value_at(cap.response, "data", name, gql_field)
            if _diff(got, expected[spec["payloadKey"]]):
                problems.append(
                    f"{api}: response {gql_field}={got!r}, expected {expected[spec['payloadKey']]!r}"
                )
        try:
            published = cap.only(s["setTopic"])
        except AssertionError as e:
            problems.append(f"{api}: {e}")
            continue
        stray = sorted(set(cap.published) - {s["setTopic"]})
        if stray:
            problems.append(f"{api}: stray publishes on {stray}")
        diffs = _diff(published, expected)
        if diffs:
            problems.append(
                f"{api}: published payload differs:\n    " + "\n    ".join(diffs[:20])
            )
        # Read-after-write: the echoed state is what both APIs now serve.
        data = _query(
            URLS[api],
            f"{{ modules {{ {module} {{ parameters {{ {gql_field} }} }} }} }}",
        )
        read = _value_at(data, "modules", module, "parameters", gql_field)
        if _diff(read, expected[spec["payloadKey"]]):
            problems.append(
                f"{api}: read-after-write {gql_field}={read!r}, expected {expected[spec['payloadKey']]!r}"
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
    query = (
        f"mutation {{ {name}({spec['argName']}: {_literal(value)}) {{ __typename }} }}"
    )
    problems = []
    for api in APIS:
        s = _spec_mutation(api, module, name)
        cap = asyncio.run(
            _run(URLS[api], query, seeds={s["stateTopic"]: json.dumps(seed)})
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
    py_name = _alias_to_name(cv_cls)[spec["payloadKey"]]
    component_cls = _bare_type(cv_cls.model_fields[py_name].annotation)
    seed_model = _seeded(cv_cls)
    args, component = _pick_component_input(
        component_cls, getattr(seed_model, py_name), spec["inputFields"]
    )
    modified = seed_model.model_copy()
    setattr(modified, py_name, component)
    seed, expected = _dump(seed_model), _dump(modified)
    shown = _selectable_leaves(
        API_SPECS[MQTT_GRAPHQL].module_mutations[module]["controlValuesObject"],
        spec["componentGqlField"],
        spec["inputFields"],
    )
    leaves_sel = " ".join(f"{leaf['argName']} {{ value timestamp }}" for leaf in shown)
    query = (
        f"mutation {{ {name}({spec['argName']}: {_input_literal(args, spec['inputFields'])}) "
        f"{{ {spec['componentGqlField']} {{ {leaves_sel} }} }} }}"
    )
    want_leaves = _expected_leaf_values(args, shown)

    problems: list[str] = []
    payloads: dict[str, Any] = {}
    for api in APIS:
        s = _spec_mutation(api, module, name)
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={s["stateTopic"]: json.dumps(seed)},
                echo={s["setTopic"]: lambda p, t=s["stateTopic"]: (t, json.dumps(p))},
            )
        )
        if cap.response.get("errors"):
            problems.append(f"{api}: mutation errored: {cap.response['errors']}")
        else:
            comp = _value_at(cap.response, "data", name, spec["componentGqlField"])
            for arg, want in want_leaves.items():
                got = comp.get(arg) or {}
                if _diff(got.get("value"), want):
                    problems.append(
                        f"{api}: response {arg}.value={got.get('value')!r}, expected {want!r}"
                    )
                if not _recent(got.get("timestamp")):
                    problems.append(
                        f"{api}: response {arg}.timestamp={got.get('timestamp')!r} not recent"
                    )
        try:
            published = cap.only(s["setTopic"])
        except AssertionError as e:
            problems.append(f"{api}: {e}")
            continue
        payloads[api] = published
        stray = sorted(set(cap.published) - {s["setTopic"]})
        if stray:
            problems.append(f"{api}: stray publishes on {stray}")
        diffs = _diff(published, expected, restamped=_restamped_keys(spec))
        if diffs:
            problems.append(
                f"{api}: published payload differs:\n    " + "\n    ".join(diffs[:20])
            )
    if len(payloads) == 2:
        diffs = _diff(
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
        MQTT_GRAPHQL, module, f"{to_camel_case(module)}SetAutomationMode"
    )
    query = (
        f"mutation {{ {spec['gqlName']}({spec['argName']}: {_literal(automatic)}) }}"
    )
    control_mode = SwitchingControlMode[desc.control_mode_cls](
        automatic_mode=_control_mode_instance(desc.control_mode_cls)
        if automatic
        else None
    )
    problems = []
    for api in APIS:
        s = _spec_mutation(api, module, spec["gqlName"])
        state = s["stateTopic"].rsplit("/", 1)[0] + "/control-mode"
        # Start from the opposite mode so the read-after-write proves a change.
        opposite = SwitchingControlMode[desc.control_mode_cls](
            automatic_mode=None
            if automatic
            else _control_mode_instance(desc.control_mode_cls)
        )
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={state: opposite.model_dump_json(by_alias=True)},
                echo={
                    s["setTopic"]: lambda _p, t=state: (
                        t,
                        control_mode.model_dump_json(by_alias=True),
                    )
                },
            )
        )
        if cap.response.get("errors"):
            problems.append(f"{api}: errored: {cap.response['errors']}")
        elif _value_at(cap.response, "data", spec["gqlName"]) is not automatic:
            problems.append(
                f"{api}: returned {cap.response['data']!r}, expected {automatic}"
            )
        try:
            published = cap.only(s["setTopic"])
        except AssertionError as e:
            problems.append(f"{api}: {e}")
            continue
        stray = sorted(set(cap.published) - {s["setTopic"]})
        if stray:
            problems.append(f"{api}: stray publishes on {stray}")
        if _diff(published, expected):
            problems.append(f"{api}: published {published!r}, expected {expected!r}")
        data = _query(
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
    return API_SPECS[api].simulation["statusTopic"], msg.model_dump_json(by_alias=True)


@pytest.mark.parametrize(("sim", "name"), _simulation_ids(), ids=lambda x: x)
def test_simulation_input_mutation_restamps_component(sim: str, name: str) -> None:
    """``{sim}SimulationSet{Component}(value: {..})``: exactly one publish on
    the simulation-inputs set topic equal to the seeded inputs object of that
    simulation with only that component replaced (restamped); response shows
    the new leaves; after the echo ``simulation.inputs`` reads them back typed
    as that simulation on both APIs."""
    mode = SIM_MODE_BY_CAMEL[sim]
    inputs_cls, _ = io_mapping[mode]
    spec = _spec_sim_mutation(MQTT_GRAPHQL, sim, name)
    sim_spec = next(
        s for s in API_SPECS[MQTT_GRAPHQL].simulation["simulations"] if s["name"] == sim
    )
    py_name = _alias_to_name(inputs_cls)[spec["payloadKey"]]
    component_cls = _bare_type(inputs_cls.model_fields[py_name].annotation)
    seed_model = _seeded(inputs_cls)
    args, component = _pick_component_input(
        component_cls, getattr(seed_model, py_name), spec["inputFields"]
    )
    modified = seed_model.model_copy()
    setattr(modified, py_name, component)
    seed, expected = _dump(seed_model), _dump(modified)
    shown = _selectable_leaves(
        sim_spec["inputs"], spec["componentGqlField"], spec["inputFields"]
    )
    leaves_sel = " ".join(f"{leaf['argName']} {{ value timestamp }}" for leaf in shown)
    query = (
        f"mutation {{ {name}({spec['argName']}: {_input_literal(args, spec['inputFields'])}) "
        f"{{ {spec['componentGqlField']} {{ {leaves_sel} }} }} }}"
    )
    want_leaves = _expected_leaf_values(args, shown)
    read_query = (
        f"{{ simulation {{ inputs {{ __typename ... on {sim_spec['inputs']['typeName']} "
        f"{{ {spec['componentGqlField']} {{ {leaves_sel} }} }} }} }} }}"
    )

    problems: list[str] = []
    payloads: dict[str, Any] = {}
    for api in APIS:
        s = _spec_sim_mutation(api, sim, name)
        status_topic, status_payload = _seed_status(api, mode, "available")
        cap = asyncio.run(
            _run(
                URLS[api],
                query,
                seeds={s["stateTopic"]: json.dumps(seed), status_topic: status_payload},
                echo={s["setTopic"]: lambda p, t=s["stateTopic"]: (t, json.dumps(p))},
            )
        )
        if cap.response.get("errors"):
            problems.append(f"{api}: mutation errored: {cap.response['errors']}")
        else:
            comp = _value_at(cap.response, "data", name, spec["componentGqlField"])
            for arg, want in want_leaves.items():
                got = comp.get(arg) or {}
                if _diff(got.get("value"), want):
                    problems.append(
                        f"{api}: response {arg}.value={got.get('value')!r}, expected {want!r}"
                    )
                if not _recent(got.get("timestamp")):
                    problems.append(
                        f"{api}: response {arg}.timestamp={got.get('timestamp')!r} not recent"
                    )
        try:
            published = cap.only(s["setTopic"])
        except AssertionError as e:
            problems.append(f"{api}: {e}")
            continue
        payloads[api] = published
        stray = sorted(set(cap.published) - {s["setTopic"]})
        if stray:
            problems.append(f"{api}: stray publishes on {stray}")
        diffs = _diff(published, expected, restamped=_restamped_keys(spec))
        if diffs:
            problems.append(
                f"{api}: published payload differs:\n    " + "\n    ".join(diffs[:20])
            )
        data = _query(URLS[api], read_query)
        inputs = _value_at(data, "simulation", "inputs")
        if inputs is None or inputs.get("__typename") != sim_spec["inputs"]["typeName"]:
            problems.append(
                f"{api}: read-after-write inputs={inputs!r}, expected {sim_spec['inputs']['typeName']}"
            )
        else:
            comp = inputs.get(spec["componentGqlField"]) or {}
            for arg, want in want_leaves.items():
                got = (comp.get(arg) or {}).get("value")
                if _diff(got, want):
                    problems.append(
                        f"{api}: read-after-write {arg}.value={got!r}, expected {want!r}"
                    )
    if len(payloads) == 2:
        diffs = _diff(
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
    inputs_cls, _ = io_mapping[mode]
    spec = _spec_sim_mutation(MQTT_GRAPHQL, sim, name)
    served_shape = _input_type_definitions()[spec["inputTypeName"]][0]
    seed = _dump(_seeded(inputs_cls))
    queries = {
        "own shape": f"mutation {{ {name}({spec['argName']}: "
        f"{_generic_input_literal(spec['inputFields'])}) {{ __typename }} }}",
        "served shape": f"mutation {{ {name}({spec['argName']}: "
        f"{_generic_input_literal(served_shape)}) {{ __typename }} }}",
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
                        s["stateTopic"]: json.dumps(seed),
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


def _directive_query(
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
        query, variables = _directive_query(name, spec, arg)
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
                        s["topic"]: lambda _p, t=status_topic, pl=expect_payload: (
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
                published = cap.only(s["topic"])
            except AssertionError as e:
                problems.append(f"{label}: {e}")
                continue
            stray = sorted(set(cap.published) - {s["topic"]})
            if stray:
                problems.append(f"{label}: stray publishes on {stray}")
            if _diff(published, expected):
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
    query, variables = _directive_query(name, spec, _directive_arg(name, spec))
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
    query, variables = _directive_query(name, spec, value)
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
    covered |= {f"{to_camel_case(m)}SetAutomationMode" for m in MODULES}
    covered |= {n for _, n in _simulation_ids()} | set(DIRECTIVES)
    covered |= {n for _, n in _colliding_simulation_ids()}
    declared: set[str] = set()
    for api in APIS:
        for module, spec in API_SPECS[api].module_mutations.items():
            for m in spec["mutations"]:
                assert m["kind"] in ("parameter", "control", "automationMode"), (
                    module,
                    m,
                )
                declared.add(m["gqlName"])
        for s in API_SPECS[api].simulation["simulations"]:
            declared |= {m["gqlName"] for m in s["mutations"]}
        declared |= {d["gqlName"] for d in API_SPECS[api].simulation["directives"]}
    assert declared == covered, {
        "not covered": sorted(declared - covered),
        "not declared": sorted(covered - declared),
    }
    assert len(covered) >= 300, f"only {len(covered)} mutations enumerated"
