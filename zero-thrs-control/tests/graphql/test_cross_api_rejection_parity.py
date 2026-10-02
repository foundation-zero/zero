"""Every write the producer's models reject is rejected alike by both APIs.

When a user enters a value the producer's models refuse - a parameter out of
its bounds, a tuning tuple of the wrong length, a value breaking a
cross-field invariant, a component leaf its model rejects, a directive
argument out of range - zero-ui shows the error's message as it comes. So for
each such write, thrs-api (5102) and zero-mqtt-graphql (5103) must answer
with the same messages (pydantic's ``ValidationError`` text) and neither may
publish anything.

Only what a client shows is compared: the messages. How the error envelope
is shaped (``path``, ``locations``, whether the field or the whole ``data``
is nulled) is each server's own, and so is the wording of errors about a
malformed request (syntax, validation, variable coercion), which the UI's
fixed documents never produce.

Needs the docker stack (vernemq, thrs-api, mqtt-graphql) and no control loop
(seeded state must hold). Nothing else may publish on the broker meanwhile: a
case fails on any publish it sees.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from tests.graphql.mutation_harness import (
    API_SPECS,
    MODULES,
    SIM_MODE_BY_CAMEL,
    _alias_to_name,
    _dump,
    _invariant_ids,
    _pick_component_input,
    _pick_invariant_violation,
    _run,
    _spec_mutation,
    _spec_sim_mutation,
    _topic,
)
from tests.graphql.parity import graphql_literal, messages
from tests.graphql.seeding import seed_state, seeded
from tests.graphql.stack_config import APIS, MQTT_GRAPHQL, THRS_API, URLS
from thrs.input_output.base import Stamped
from thrs.runtime.descriptions.simulation import simulation_io_classes
from thrs.spec.extension import component_class

pytestmark = pytest.mark.migration


@pytest.fixture(scope="module", autouse=True)
def seeded_state(docker_stack: None) -> None:
    """One complete state on both prefix sets (``tests.graphql.seeding``)."""
    seed_state()


# The owner of a simulation member's mutations (member names repeat module names).
SIMULATION_OWNER = "simulation:"


def _mutations() -> list[tuple[str, dict[str, Any]]]:
    """(owner, spec) for every mutation both specs declare: module members'
    and simulation members'."""
    spec = API_SPECS[MQTT_GRAPHQL]
    out = [
        (module, m)
        for module, member in sorted(spec.members.items())
        for m in member["mutations"]
    ]
    out += [
        (f"{SIMULATION_OWNER}{s['name']}", m)
        for s in spec.simulation["members"]
        for m in s["mutations"]
    ]
    return out


@dataclass(frozen=True)
class Rejection:
    """A write the producer's models reject: the document, and the retained
    state each API needs cached (per API, on its own prefixes)."""

    query: str
    seeds: dict[str, dict[str, str]]


def _parameter_seeds(module: str, name: str) -> dict[str, dict[str, str]]:
    seed = json.dumps(_dump(MODULES[module].parameters_cls()))
    return {
        api: {_topic(api, _spec_mutation(api, module, name)["state"]): seed}
        for api in APIS
    }


# Values a parameter is tried with; the ones its parameters model rejects on
# assignment (bounds, clamps, cross-field invariants) become cases.
PARAMETER_PROBES = (-1e6, 1e6)


def _parameter_rejects(params_cls: Any, py_name: str, value: Any) -> bool:
    try:
        setattr(params_cls(), py_name, value)
    except ValidationError:
        return True
    return False


def _parameter_rejections() -> dict[str, Rejection]:
    cases: dict[str, Rejection] = {}
    for module, member in sorted(API_SPECS[MQTT_GRAPHQL].members.items()):
        params_cls = MODULES[module].parameters_cls
        aliases = _alias_to_name(params_cls)
        tuple_done = False
        for m in member["mutations"]:
            if m["kind"] != "setField":
                continue
            name, py_name = m["gql"], aliases[m["key"]]
            if m["argType"].startswith("["):
                if tuple_done:
                    continue
                tuple_done = True
                probes = {
                    "tuple short": [1.0],
                    "tuple long": [1.0, 2.0, 3.0, 4.0],
                    "tuple empty": [],
                }
            elif m["argType"] == "Float":
                probes = {
                    str(v): v
                    for v in PARAMETER_PROBES
                    if _parameter_rejects(params_cls, py_name, v)
                }
            else:
                continue
            for label, value in probes.items():
                cases[f"{module}.{name} {label}"] = Rejection(
                    f"mutation {{ {name}(value: {graphql_literal(value)}) {{ __typename }} }}",
                    _parameter_seeds(module, name),
                )
    for module, name in _invariant_ids():
        params_cls = MODULES[module].parameters_cls
        spec = _spec_mutation(MQTT_GRAPHQL, module, name)
        picked = _pick_invariant_violation(
            params_cls, _alias_to_name(params_cls)[spec["key"]], spec["invariants"]
        )
        if picked is not None:
            cases[f"{module}.{name} invariant"] = Rejection(
                f"mutation {{ {name}(value: {graphql_literal(float(picked[0]))}) {{ __typename }} }}",
                _parameter_seeds(module, name),
            )
    return cases


# Values a component input leaf is tried with; the ones the component's own
# model rejects become cases.
LEAF_PROBES = (-1e6, 0.05, 1e6)


def _component_rejections() -> dict[str, Rejection]:
    """Per component input type (validation is the component model's), each
    numeric leaf with every probe value the model rejects - the other leaves
    at accepted values."""
    cases: dict[str, Rejection] = {}
    seen_types: set[str] = set()
    for owner, m in [
        (o, m)
        for o, m in _component_mutations()
        if m["inputTypeName"] not in seen_types
    ]:
        seen_types.add(m["inputTypeName"])
        container_cls, seeds = _component_container(owner, m)
        py_name = _alias_to_name(container_cls)[m["key"]]
        component_cls = component_class(container_cls.model_fields[py_name].annotation)
        seed_model = seeded(container_cls)
        try:
            args, _ = _pick_component_input(
                component_cls, getattr(seed_model, py_name), m["inputFields"]
            )
        except AssertionError:
            continue
        for leaf in m["inputFields"]:
            if leaf["type"] != "Float":
                continue
            for probe in LEAF_PROBES:
                if not _component_rejects(component_cls, m, args, leaf["gql"], probe):
                    continue
                trial = {**args, leaf["gql"]: probe}
                literal = ", ".join(
                    f"{f['gql']}: {graphql_literal(f['enumValues'][str(trial[f['gql']])] if f.get('enumValues') else trial[f['gql']])}"
                    for f in m["inputFields"]
                    if f["gql"] in trial
                )
                cases[f"{owner}.{m['gql']} {leaf['gql']}={probe}"] = Rejection(
                    f"mutation {{ {m['gql']}(value: {{{literal}}}) {{ __typename }} }}",
                    seeds,
                )
    return cases


def _component_mutations() -> list[tuple[str, dict[str, Any]]]:
    return [(o, m) for o, m in _mutations() if m["kind"] == "setComponent"]


def _component_container(
    owner: str, m: dict[str, Any]
) -> tuple[Any, dict[str, dict[str, str]]]:
    """The whole object the component lives in and its seeds per API."""
    if not owner.startswith(SIMULATION_OWNER):
        cls = MODULES[owner].control_values_cls
        seed = json.dumps(_dump(seeded(cls)))
        return cls, {
            api: {_topic(api, _spec_mutation(api, owner, m["gql"])["state"]): seed}
            for api in APIS
        }
    sim = owner.removeprefix(SIMULATION_OWNER)
    cls, _ = simulation_io_classes()[SIM_MODE_BY_CAMEL[sim]]
    seed = json.dumps(_dump(seeded(cls)))
    return cls, {
        api: {_topic(api, _spec_sim_mutation(api, sim, m["gql"])["state"]): seed}
        for api in APIS
    }


def _component_rejects(
    component_cls: Any, m: dict[str, Any], args: dict[str, Any], gql: str, probe: float
) -> bool:
    """Whether the component model rejects ``args`` with ``gql`` set to
    ``probe`` (built the way the API builds it: every leaf stamped now)."""
    by_gql = {f["gql"]: f for f in m["inputFields"]}
    aliases = _alias_to_name(component_cls)
    now = datetime.now(UTC)
    values = {**args, gql: probe}
    stamped = {
        aliases[by_gql[g]["key"]]: Stamped(value=v, timestamp=now)
        for g, v in values.items()
    }
    try:
        component_cls(**stamped)
    except ValidationError:
        return True
    return False


def _directive_rejections() -> dict[str, Rejection]:
    cases: dict[str, Rejection] = {}
    for d in API_SPECS[MQTT_GRAPHQL].simulation["directives"]:
        for side, bound in (d.get("bounds") or {}).items():
            value = {"min": bound - 0.1, "max": bound + 1.0}.get(side)
            if value is None:
                continue
            cases[f"{d['gql']} {side}"] = Rejection(
                f"mutation {{ {d['gql']}({d['argName']}: {graphql_literal(float(value))}) }}",
                {api: {} for api in APIS},
            )
    return cases


REJECTIONS = {
    **_parameter_rejections(),
    **_component_rejections(),
    **_directive_rejections(),
}


@pytest.mark.parametrize("case", sorted(REJECTIONS))
def test_model_rejection_parity(case: str) -> None:
    """The producer's models reject the write: both APIs answer with the
    same pydantic error messages and publish nothing."""
    rejection = REJECTIONS[case]
    answers: dict[str, list[str]] = {}
    for api in APIS:
        capture = asyncio.run(
            _run(URLS[api], rejection.query, seeds=rejection.seeds[api])
        )
        assert not capture.published, (
            f"{api} published {capture.published!r} for {case}"
        )
        answers[api] = messages(capture.response)
        assert answers[api], f"{api} accepted {case}: {capture.response!r}"
    if len(answers) == 2:
        assert answers[THRS_API] == answers[MQTT_GRAPHQL], (
            f"{case}\n thrs-api     {answers[THRS_API]}\n"
            f" mqtt-graphql {answers[MQTT_GRAPHQL]}"
        )


def test_rejections_cover_every_kind() -> None:
    """Guard against a silent gap: parameter bounds, tuning tuples, invariants,
    component leaves and directive bounds each yield cases."""
    assert any(" tuple " in c for c in REJECTIONS)
    assert any(" invariant" in c for c in REJECTIONS)
    assert any("=" in c for c in REJECTIONS)
    assert any(c.startswith("simulationPlay") for c in REJECTIONS)
