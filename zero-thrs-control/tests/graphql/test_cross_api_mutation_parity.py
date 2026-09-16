"""Cross-API *write* parity: the same GraphQL mutation, given to thrs-api (5102)
and to zero-mqtt-graphql (5103), must publish the *same thing* to MQTT.

Where ``test_cross_api_parity*.py`` prove read parity, this proves the write
half of the migration: zero-ui issues the same mutations against whichever API
it points at, so both must translate a mutation into an identical MQTT publish
(same topic, same payload). The mqtt-graphql side runs for every module in
``MQTT_GRAPHQL_MUTATIONS_READY`` (all of them today); the thrs-api side always
runs, so the contract each mutation must meet is pinned here regardless.

The contract (confirmed empirically against the running stack, see
``ControlApiChannels`` in ``thrs.orchestration.comms``):

* A parameter mutation ``{module}ParameterSet{Field}(value: X)`` reads the
  current parameters, sets one field, and publishes the *whole* parameters
  object to ``{controller_prefix}/{module}/parameters/set`` as
  ``model_dump_json(by_alias=True)``.
* A manual-control mutation ``{module}ControlSet{Field}(value: X)`` does the same
  for control values -> ``{controller_prefix}/{module}/manual-values/set``.
* ``{module}SetAutomationMode(automatic: b)`` publishes an ``AutomationMode`` to
  ``{controller_prefix}/{module}/automation-mode/set``.

Self-contained without a ticking control loop: the API's mutation first reads the
*state* topic (``.../parameters`` etc., normally published by the controller)
and then waits to read its own change back. We seed those state topics with the
post-mutation value up front, so ``get_*``/``wait_for_*`` succeed immediately and
the mutation runs to its publish, which is what we capture and compare. The
publish is non-retained, so the capture only sees what this mutation emitted.

Prefixes differ in the running stack (thrs-api's docker-compose env vs the
specs' defaults, see ``stack_config``); each API is seeded and captured on its
own prefix.

Run from ``zero-thrs-control/`` with the stack up::

    uv run pytest tests/graphql/test_cross_api_mutation_parity.py
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx
import pytest
from aiomqtt import Client as MqttClient

from tests.graphql.stack_config import mqtt_graphql_config, thrs_api_config
from thrs.graphql.messaging import PARAMETERS_TIMEOUT_ERROR
from thrs.spec.asyncapi import all_module_descriptions, build_module_mutations

MQTT_HOST = "localhost"
MQTT_PORT = 1883
THRS_API_URL = "http://localhost:5102/graphql"
MQTT_GRAPHQL_URL = "http://localhost:5103/graphql"

THRS_API_CONTROLLER_PREFIX = thrs_api_config().mqtt_controller_topic_prefix
MQTT_GRAPHQL_CONTROLLER_PREFIX = mqtt_graphql_config().mqtt_controller_topic_prefix

# Modules whose zero-mqtt-graphql mutation (write) path is implemented and
# verified. Empty until the write-path lands: while a module is missing here its
# mqtt-graphql assertions skip and only the thrs-api contract is checked.
MQTT_GRAPHQL_MUTATIONS_READY: frozenset[str] = frozenset(
    {"thrusters", "adsorption", "consumers", "dc", "dhw", "drives", "pcm", "pvt"}
)

# Float leaves in a published payload: tolerant compare (Python vs Rust format
# f64s differently by ~1 ULP). Mirrors the read suite's FLOAT_EXACT_MATCH.
FLOAT_EXACT_MATCH = False
FLOAT_REL_TOL = 1e-9


# --- The mutation contract cases -------------------------------------------


@dataclass(frozen=True)
class MutationCase:
    """One mutation and the MQTT publish it must produce."""

    name: str
    module: str
    mutation: str
    """GraphQL mutation body, e.g. `thrustersParameterSetCoolingFlow(value: 12.34)`."""
    selection: str
    """Selection set for the mutation's return type (payload-shape only)."""
    set_topic_suffix: str
    """Topic under `{controller_prefix}/{module}/`, e.g. `parameters/set`."""
    seed_state_suffix: str | None
    """State topic (no `/set`) to seed so the API's read/echo succeeds, or None
    (automation-mode seeds `control-mode`, handled specially)."""
    build_seed: Callable[[], str]
    """Returns the retained state payload to seed (JSON string)."""
    expected_payload: Callable[[], dict[str, Any]]
    """The JSON body the mutation must publish to `set_topic_suffix`."""
    thrs_api_echo_timeout: bool = False
    """thrs-api publishes but then errors with "Timeout when setting parameters":
    a tuning (tuple) parameter never echoes back equal, because
    ``ControlMessaging.set_parameter`` compares the model's ``tuple`` against the
    mutation's ``list`` argument (thrs-api quirk). The published payload is still
    the contract; mqtt-graphql needn't reproduce the spurious error."""


THRS_API_ECHO_TIMEOUT = PARAMETERS_TIMEOUT_ERROR


def _literal(value: Any) -> str:
    """GraphQL literal for a mutation argument."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    return repr(value)


def _all_cases() -> tuple[MutationCase, ...]:
    """Every scalar parameter mutation of every module, built from
    ``build_module_mutations`` (the same contract mqtt-graphql consumes) and the
    module's default parameters object. Exhaustive by construction, like the read
    parity suite: a new scalar parameter is covered the moment it appears.

    Each mutation sets its field to that field's own default value. That is the
    one value guaranteed to satisfy the parameters model's *cross-field*
    invariants (e.g. "recovery temperature must exceed warmup temperature"),
    which thrs-api enforces on assignment and would reject for an arbitrary
    number. This checks the write mechanism end to end -- read the state,
    republish the whole object to the right topic, byte-for-byte alike on both
    APIs. That mqtt-graphql *changes* a field is covered by its Rust unit test;
    that it rejects the same out-of-range values thrs-api does is covered by the
    ``bounds`` in the mutations spec (Rust unit test); the cross-field
    invariants a parameters model enforces in a ``model_validator`` are not
    reproduced by mqtt-graphql (known gap).

    The seed state carries the (unchanged) default object, so the API's
    ``wait_for_parameters`` matches at once without a running controller."""
    cases: list[MutationCase] = []
    for module, desc in sorted(all_module_descriptions().items()):
        try:
            base = json.loads(desc.parameters_cls().model_dump_json(by_alias=True))
        except Exception:  # noqa: BLE001 - a params model that needs args; skip
            continue
        for m in build_module_mutations(module)["mutations"]:
            # This exhaustive byte-compare suite covers only `parameter`
            # mutations (single scalar into the parameters object). `control`
            # (composite input) and `automationMode` are a different shape -
            # control payloads carry read-time `now()` timestamps that can't be
            # byte-compared - and are covered by the Rust unit tests and the live
            # probes instead.
            if m["kind"] != "parameter":
                continue
            target = base[m["payloadKey"]]  # the field's own default: always valid
            expected = {**base, m["payloadKey"]: target}
            cases.append(
                MutationCase(
                    name=f"{module}_{m['payloadKey']}",
                    module=module,
                    mutation=f"{m['gqlName']}(value: {_literal(target)})",
                    selection="__typename",
                    set_topic_suffix="parameters/set",
                    seed_state_suffix="parameters",
                    build_seed=(lambda e=expected: json.dumps(e)),
                    expected_payload=(lambda e=expected: e),
                    thrs_api_echo_timeout=m["argType"].startswith("["),
                )
            )
    return tuple(cases)


# Only `parameter` mutations so far. Extension points (validated contract):
#   * manual-control: `{module}ControlSet{Field}` -> `manual-values/set`.
#   * automation-mode: `{module}SetAutomationMode(automatic:)` ->
#     `automation-mode/set` (seed `control-mode` state).
CASES: tuple[MutationCase, ...] = _all_cases()


# --- MQTT capture -----------------------------------------------------------


async def _capture_during(
    action: Callable[[], httpx._models.Response],
    seed_topic: str | None,
    seed_payload: str | None,
    settle: float = 2.0,
) -> tuple[dict[str, str], str]:
    """Seed a retained state topic, then capture every non-retained publish
    while ``action`` (the mutation POST) runs. Returns {topic: payload} of the
    publishes seen and the GraphQL response text."""
    captured: dict[str, str] = {}
    async with MqttClient(MQTT_HOST, MQTT_PORT) as client:
        if seed_topic is not None and seed_payload is not None:
            await client.publish(seed_topic, payload=seed_payload, retain=True)
        await client.subscribe("#")

        async def _drain() -> None:
            async for msg in client.messages:
                if not msg.retain:
                    captured[str(msg.topic)] = msg.payload.decode()

        task = asyncio.create_task(_drain())
        await asyncio.sleep(0.5)
        response = await asyncio.to_thread(action)
        await asyncio.sleep(settle)
        task.cancel()
    return captured, response.text


def _post(url: str, query: str) -> httpx._models.Response:
    return httpx.post(url, json={"query": query}, timeout=15.0)


def _mutation_query(case: MutationCase, *, with_selection: bool = True) -> str:
    """Build the mutation query. A parameter mutation now returns the parameters
    object on *both* APIs (mqtt-graphql builds a per-module return type resolved
    off the object it just published), so both take the same selection set. The
    mutation's asserted contract is the MQTT publish it makes; the selection only
    has to make the query valid for an object return."""
    body = f"{{ {case.selection} }}" if with_selection and case.selection else ""
    return f"mutation {{ {case.mutation} {body} }}"


def _payloads_equal(a: Any, b: Any) -> bool:
    """Deep compare two JSON values, floats within tolerance unless exact."""
    import math

    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_payloads_equal(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_payloads_equal(x, y) for x, y in zip(a, b))
    if not FLOAT_EXACT_MATCH and isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=FLOAT_REL_TOL, abs_tol=1e-12)
    return a == b


# --- Tests ------------------------------------------------------------------


def _assert_thrs_api_response(case: MutationCase, body: dict[str, Any]) -> None:
    errors = body.get("errors")
    if case.thrs_api_echo_timeout:
        assert errors and errors[0]["message"] == THRS_API_ECHO_TIMEOUT, (
            f"expected thrs-api's echo timeout for a tuning mutation, got {body!r}"
        )
        return
    assert not errors, f"thrs-api mutation errored: {errors}"


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_thrs_api_mutation_publishes_expected(case: MutationCase) -> None:
    """Contract (thrs-api side, always on): the mutation publishes the expected
    full object to `{controller_prefix}/{module}/{set_topic_suffix}`."""
    prefix = THRS_API_CONTROLLER_PREFIX
    set_topic = f"{prefix}/{case.module}/{case.set_topic_suffix}"
    seed_topic = (
        f"{prefix}/{case.module}/{case.seed_state_suffix}"
        if case.seed_state_suffix
        else None
    )

    captured, resp_text = asyncio.run(
        _capture_during(
            lambda: _post(THRS_API_URL, _mutation_query(case)),
            seed_topic,
            case.build_seed() if case.seed_state_suffix else None,
        )
    )
    body = json.loads(resp_text)
    _assert_thrs_api_response(case, body)
    assert set_topic in captured, (
        f"thrs-api did not publish to {set_topic!r}; saw {sorted(captured)!r}"
    )
    published = json.loads(captured[set_topic])
    expected = case.expected_payload()
    assert _payloads_equal(published, expected), (
        f"{case.name}: published payload != expected\n"
        f"published={published!r}\nexpected={expected!r}"
    )


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_mutation_parity_thrs_api_vs_mqtt_graphql(case: MutationCase) -> None:
    """1:1 write parity: the same mutation publishes an identical payload from
    both APIs. Skipped per module until its mqtt-graphql write-path lands."""
    if case.module not in MQTT_GRAPHQL_MUTATIONS_READY:
        pytest.skip(
            f"mqtt-graphql write-path for {case.module!r} not implemented yet; add "
            f"it to MQTT_GRAPHQL_MUTATIONS_READY once its mutations publish 1:1."
        )

    thrs_set = f"{THRS_API_CONTROLLER_PREFIX}/{case.module}/{case.set_topic_suffix}"
    mqtt_set = f"{MQTT_GRAPHQL_CONTROLLER_PREFIX}/{case.module}/{case.set_topic_suffix}"

    thrs_captured, thrs_resp = asyncio.run(
        _capture_during(
            lambda: _post(THRS_API_URL, _mutation_query(case)),
            f"{THRS_API_CONTROLLER_PREFIX}/{case.module}/{case.seed_state_suffix}"
            if case.seed_state_suffix
            else None,
            case.build_seed() if case.seed_state_suffix else None,
        )
    )
    mqtt_captured, mqtt_resp = asyncio.run(
        _capture_during(
            # Parameter mutations now return the parameters object on both APIs.
            lambda: _post(MQTT_GRAPHQL_URL, _mutation_query(case)),
            f"{MQTT_GRAPHQL_CONTROLLER_PREFIX}/{case.module}/{case.seed_state_suffix}"
            if case.seed_state_suffix
            else None,
            case.build_seed() if case.seed_state_suffix else None,
        )
    )
    _assert_thrs_api_response(case, json.loads(thrs_resp))
    assert "errors" not in json.loads(mqtt_resp), mqtt_resp
    assert thrs_set in thrs_captured, sorted(thrs_captured)
    assert mqtt_set in mqtt_captured, sorted(mqtt_captured)
    assert _payloads_equal(
        json.loads(thrs_captured[thrs_set]), json.loads(mqtt_captured[mqtt_set])
    ), (
        f"{case.name}: payloads differ between APIs\n"
        f"thrs-api={thrs_captured[thrs_set]}\nmqtt-graphql={mqtt_captured[mqtt_set]}"
    )
