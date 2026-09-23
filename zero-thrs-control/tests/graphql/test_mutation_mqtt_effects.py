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
import time
from datetime import UTC, datetime
from typing import Any

import pytest

from tests.graphql.mutation_harness import (
    API_SPECS,
    APIS,
    DIRECTIVES,
    MODULES,
    SIM_MODE_BY_CAMEL,
    _alias_to_name,
    _automation_ids,
    _bounded_parameter_ids,
    _colliding_simulation_ids,
    _control_ids,
    _directive_ids,
    _directive_rejections,
    _dump,
    _expected_leaf_values,
    _generic_inputgraphql_literal,
    _input_type_definitions,
    _inputgraphql_literal,
    _invariant_ids,
    _parameter_ids,
    _pick_component_input,
    _pick_invariant_violation,
    _pick_parameter_value,
    _restamped_keys,
    _run,
    _selectable_leaves,
    _simulation_ids,
    _spec_directive,
    _spec_mutation,
    _spec_sim_mutation,
    _topic,
    _value_at,
    diff_,
    recent_,
)
from tests.graphql.parity import graphql_literal, query_data
from tests.graphql.resolved import section_of
from tests.graphql.seeding import control_mode_instance, seeded
from tests.graphql.stack_config import (
    MQTT_GRAPHQL,
    THRS_API,
    URLS,
)
from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import ThrsValues
from thrs.runtime.descriptions.simulation import simulation_io_classes
from thrs.runtime.messages import SimulationStatusMessage
from thrs.spec import contract
from thrs.spec.extension import component_class
from thrs.spec.naming import field_name

pytestmark = pytest.mark.migration


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
