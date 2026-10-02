"""Every mutation the UI can send, sent the way the UI sends it.

The mutation suites build their own documents (inline literals, their own
selections). zero-ui sends different ones: a form posts
``mutation ($input: <InputType>) { <mutation>(value: $input) { <the section's
query fragment> } }`` with the value in a *variable*, only the fields that
form edits, and the whole section read back; the automation switch and the
simulation directives use ``mutationWithValue``/``mutationWithoutValue``;
the advisory switch its own template. This suite takes those templates, the
fragments and each form's fields from the UI's source (``ui_source``) and
sends every mutation the UI can issue - each parameter, each component with a
form, each automation switch, the advisory switch, play/pause/step - to both
APIs, playing the controller's echo, and asserts both answer with the same
response and publish the same payload.

Known, accepted difference (user decision): a tuning tuple (``[Float!]!``)
times out on thrs-api (its echo check compares a tuple with a list) while
mqtt-graphql confirms it; the publishes are still identical.

Needs the docker stack (vernemq, thrs-api, mqtt-graphql) and no control loop.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pytest

from tests.graphql.mutation_harness import (
    API_SPECS,
    APIS,
    MODULES,
    SIM_MODE_BY_CAMEL,
    Echo,
    _alias_to_name,
    _dump,
    _pick_component_input,
    _pick_parameter_value,
    _restamped_keys,
    _run,
    _spec_directive,
    _spec_mutation,
    _spec_sim_mutation,
    _topic,
    diff_,
)
from tests.graphql.parity import diff
from tests.graphql.seeding import control_mode_instance, seeded
from tests.graphql.stack_config import MQTT_GRAPHQL, THRS_API, URLS
from tests.graphql.ui_source import (
    advisory_mutation,
    automation_call,
    directive_calls,
    form_inputs,
    form_mutation,
    module_queries,
    mutation_with_value,
    mutation_without_value,
    simulation_input_queries,
)
from thrs.control.switching import SwitchingControlMode
from thrs.runtime.descriptions.simulation import simulation_io_classes
from thrs.runtime.messages import SimulationStatusMessage
from thrs.spec import contract
from thrs.spec.extension import component_class
from thrs.spec.naming import field_name

pytestmark = pytest.mark.migration

# Restamped leaves carry each API's own now(); within this window they match.
NOW_WINDOW_S = 60.0
ADVISORY_INPUT_TYPE = "AmcsControlModeInputType"


@dataclass(frozen=True)
class UiCall:
    """One mutation as the UI sends it, with what each API needs around it:
    per API the retained seeds and the controller's echo."""

    query: str
    variables: dict[str, Any] | None
    seeds: dict[str, dict[str, str]]
    echo: dict[str, dict[str, Echo]]
    restamped: frozenset[str] = frozenset()
    # thrs-api's echo check never matches a tuning tuple (accepted
    # difference, see the module docstring).
    thrs_api_times_out: bool = False


def _echo_state(api: str, spec: dict[str, Any]) -> dict[str, Echo]:
    state = _topic(api, spec["state"])
    return {_topic(api, spec["target"]): lambda p, t=state: (t, json.dumps(p))}


def _enum_member(leaf: dict[str, Any], value: Any) -> Any:
    return leaf["enumValues"][str(value)] if leaf.get("enumValues") else value


# --- The calls ----------------------------------------------------------------------


def _parameter_calls() -> dict[str, UiCall]:
    forms = form_inputs()
    queries = module_queries()
    calls: dict[str, UiCall] = {}
    for module, member in sorted(API_SPECS[MQTT_GRAPHQL].members.items()):
        params_cls = MODULES[module].parameters_cls
        aliases = _alias_to_name(params_cls)
        seed = json.dumps(_dump(params_cls()))
        for m in member["mutations"]:
            if m["kind"] != "setField":
                continue
            is_list = m["argType"].startswith("[")
            input_type = f"[{m['argType'][1:-2]}!]!" if is_list else f"{m['argType']}!"
            if input_type not in forms:
                continue
            value, _, _ = _pick_parameter_value(params_cls, aliases[m["key"]])
            specs = {api: _spec_mutation(api, module, m["gql"]) for api in APIS}
            calls[f"{module}.{m['gql']}"] = UiCall(
                query=form_mutation(
                    input_type, m["gql"], queries[module]["parameters"]
                ),
                variables={"input": list(value) if is_list else value},
                seeds={api: {_topic(api, specs[api]["state"]): seed} for api in APIS},
                echo={api: _echo_state(api, specs[api]) for api in APIS},
                thrs_api_times_out=is_list,
            )
    return calls


def _component_call(
    container_cls: Any,
    m: dict[str, Any],
    specs: dict[str, dict[str, Any]],
    query: str,
    extra_seeds: dict[str, dict[str, str]],
    fields: list[str],
) -> UiCall:
    py_name = _alias_to_name(container_cls)[m["key"]]
    component_cls = component_class(container_cls.model_fields[py_name].annotation)
    seed_model = seeded(container_cls)
    args, _ = _pick_component_input(
        component_cls, getattr(seed_model, py_name), m["inputFields"]
    )
    by_gql = {leaf["gql"]: leaf for leaf in m["inputFields"]}
    variables = {
        "input": {f: _enum_member(by_gql[f], args[f]) for f in fields if f in by_gql}
    }
    seed = json.dumps(_dump(seed_model))
    return UiCall(
        query=query,
        variables=variables,
        seeds={
            api: {_topic(api, specs[api]["state"]): seed, **extra_seeds[api]}
            for api in APIS
        },
        echo={api: _echo_state(api, specs[api]) for api in APIS},
        restamped=frozenset(_restamped_keys(m)),
    )


def _control_calls() -> dict[str, UiCall]:
    forms = form_inputs()
    queries = module_queries()
    calls: dict[str, UiCall] = {}
    for module, member in sorted(API_SPECS[MQTT_GRAPHQL].members.items()):
        for m in member["mutations"]:
            input_type = f"{m.get('inputTypeName')}!"
            if m["kind"] != "setComponent" or input_type not in forms:
                continue
            specs = {api: _spec_mutation(api, module, m["gql"]) for api in APIS}
            calls[f"{module}.{m['gql']}"] = _component_call(
                MODULES[module].control_values_cls,
                m,
                specs,
                form_mutation(input_type, m["gql"], queries[module]["controlValues"]),
                {api: {} for api in APIS},
                forms[input_type],
            )
    return calls


def _status_seed(api: str, mode: str, status: str) -> dict[str, str]:
    message = SimulationStatusMessage(
        mode=mode,
        status=status,  # type: ignore[arg-type]
        control_modules=[mode],
        simulation_time=datetime(2026, 1, 2, 3, 4, 5, 678901, tzinfo=UTC),
    )
    topic = _topic(api, API_SPECS[api].simulation["status"]["operation"])
    return {topic: message.model_dump_json(by_alias=True)}


def _simulation_calls() -> dict[str, UiCall]:
    forms = form_inputs()
    queries = simulation_input_queries()
    calls: dict[str, UiCall] = {}
    for member in API_SPECS[MQTT_GRAPHQL].simulation["members"]:
        sim = member["name"]
        mode = SIM_MODE_BY_CAMEL[sim]
        inputs_cls, _ = simulation_io_classes()[mode]
        for m in member["mutations"]:
            input_type = f"{m['inputTypeName']}!"
            if m["inputTypeName"] == ADVISORY_INPUT_TYPE:
                query = advisory_mutation(m["gql"], queries[sim])
                fields = [leaf["gql"] for leaf in m["inputFields"]]
            elif input_type in forms:
                query = form_mutation(input_type, m["gql"], queries[sim])
                fields = forms[input_type]
            else:
                continue
            specs = {api: _spec_sim_mutation(api, sim, m["gql"]) for api in APIS}
            calls[f"{sim}.{m['gql']}"] = _component_call(
                inputs_cls,
                m,
                specs,
                query,
                {api: _status_seed(api, mode, "available") for api in APIS},
                fields,
            )
    return calls


def _automation_calls() -> dict[str, UiCall]:
    arg, value_type = automation_call()
    calls: dict[str, UiCall] = {}
    for module in sorted(MODULES):
        desc = MODULES[module]
        name = f"{field_name(module)}SetAutomationMode"
        for automatic in (True, False):
            confirmed = SwitchingControlMode[desc.control_mode_cls](
                automatic_mode=control_mode_instance(desc.control_mode_cls)
                if automatic
                else None
            )
            opposite = SwitchingControlMode[desc.control_mode_cls](
                automatic_mode=None
                if automatic
                else control_mode_instance(desc.control_mode_cls)
            )
            specs = {api: _spec_mutation(api, module, name) for api in APIS}
            confirm = {
                api: _topic(api, specs[api]["confirm"]["operation"]) for api in APIS
            }
            calls[f"{module}.{name}({automatic})"] = UiCall(
                query=mutation_with_value(name, arg, value_type),
                variables={"value": automatic},
                seeds={
                    api: {confirm[api]: opposite.model_dump_json(by_alias=True)}
                    for api in APIS
                },
                echo={
                    api: {
                        _topic(
                            api, specs[api]["target"]
                        ): lambda _p, t=confirm[api], c=confirmed: (
                            t,
                            c.model_dump_json(by_alias=True),
                        )
                    }
                    for api in APIS
                },
            )
    return calls


def _directive_calls() -> dict[str, UiCall]:
    calls: dict[str, UiCall] = {}
    by_name = {d.message.subscribe_topic(): d for d in contract.SIMULATION_DIRECTIVES}
    mode = SIM_MODE_BY_CAMEL[API_SPECS[MQTT_GRAPHQL].simulation["members"][0]["name"]]
    for name, call in directive_calls().items():
        specs = {api: _spec_directive(api, name) for api in APIS}
        directive = by_name[
            _topic(MQTT_GRAPHQL, specs[MQTT_GRAPHQL]["target"]).rsplit("/", 1)[1]
        ]
        if call is None:
            query, variables = mutation_without_value(name), None
        else:
            arg, value_type = call
            query = mutation_with_value(name, arg, value_type)
            variables = {"value": 2.0}
        calls[name] = UiCall(
            query=query,
            variables=variables,
            seeds={
                api: _status_seed(api, mode, directive.allowed_from[0]) for api in APIS
            },
            echo={
                api: {
                    _topic(
                        api, specs[api]["target"]
                    ): lambda _p, a=api, s=directive.expect_status: next(
                        iter(_status_seed(a, mode, s).items())
                    )
                }
                for api in APIS
            },
        )
    return calls


CALLS = {
    **_parameter_calls(),
    **_control_calls(),
    **_simulation_calls(),
    **_automation_calls(),
    **_directive_calls(),
}


@pytest.mark.parametrize("case", sorted(CALLS))
def test_ui_mutation_parity(case: str) -> None:
    """The UI's own document, variables and selection: both APIs answer the
    same and publish the same payload."""
    call = CALLS[case]
    captures = {
        api: asyncio.run(
            _run(
                URLS[api],
                call.query,
                seeds=call.seeds[api],
                echo=call.echo[api],
                variables=call.variables,
            )
        )
        for api in APIS
    }
    problems: list[str] = []
    for api, capture in captures.items():
        errors = capture.response.get("errors")
        timeout = [{"message": contract.PARAMETERS_TIMEOUT_ERROR}]
        if api == THRS_API and call.thrs_api_times_out:
            if [{"message": e["message"]} for e in errors or []] != timeout:
                problems.append(f"{api}: expected its tuning timeout, got {errors!r}")
        elif errors:
            problems.append(f"{api}: errored: {errors!r}")
        if len(capture.published) != 1:
            problems.append(
                f"{api}: published {sorted(capture.published)!r}, expected one topic"
            )
    if len(captures) == 2 and not problems:
        a, b = captures[THRS_API], captures[MQTT_GRAPHQL]
        if not call.thrs_api_times_out:
            problems += diff(a.response, b.response, now_window_s=NOW_WINDOW_S)
        (pa,) = a.published.values()
        (pb,) = b.published.values()
        problems += [
            f"published {d}" for d in diff_(pa[0], pb[0], restamped=set(call.restamped))
        ]
    assert not problems, f"{case}:\n" + "\n".join(problems[:40])


def test_every_ui_form_is_exercised() -> None:
    """Guard against a silent gap: every input type a UI form sends and every
    directive the UI sends appears in at least one call."""
    queries = " ".join(call.query for call in CALLS.values())
    for input_type in form_inputs():
        assert f"$input: {input_type}" in queries, f"no call sends {input_type}"
    for name in directive_calls():
        assert name in CALLS, f"directive {name} not exercised"
