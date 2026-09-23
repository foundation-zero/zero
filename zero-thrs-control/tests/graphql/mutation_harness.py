"""The per-mutation case model and MQTT harness the mutation suites share.

Every case is derived from the contract each API is generated for
(``ResolvedSpec`` per prefix set) and from THRS's own pydantic models - no
topic, key or value is typed by hand. ``_run`` seeds retained state, sends a
request and captures what the API publishes, playing the controller's echo
where asked (see ``test_mutation_mqtt_effects``).
"""

from __future__ import annotations

import asyncio
import json
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from aiomqtt import Client as MqttClient
from pydantic import TypeAdapter, ValidationError

from tests.graphql.parity import diff, graphql_literal, post, recent
from tests.graphql.resolved import ResolvedSpec
from tests.graphql.stack_config import (
    MQTT_GRAPHQL,
    MQTT_HOST,
    MQTT_PORT,
    THRS_API,
    URLS,
    mqtt_graphql_config,
    selected_apis,
    thrs_api_config,
)
from thrs.input_output.base import Stamped, ThrsValues
from thrs.runtime.descriptions.simulation import simulation_io_classes
from thrs.spec import contract
from thrs.spec.asyncapi import all_module_descriptions
from thrs.spec.naming import field_name

APIS = selected_apis()

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
