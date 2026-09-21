"""Exhaustive cross-API read-parity: thrs-api (5102) vs zero-mqtt-graphql (5103).

Where ``test_cross_api_parity.py`` proves the idea on three hand-picked
thrusters fields, this suite is exhaustive by construction: it walks every
module the contract declares and, per module, every ``sensorValues`` field and
every ``{value, timestamp}`` leaf, i.e. the surface the UI reads via
``modules.<module>.sensorValues.<field>.<leaf>`` (zero-ui's ``QUERY_ALL`` /
``*_SENSOR_QUERY``). New fields are covered the moment they appear on a model,
with no hand-maintained list to drift.

The target is 1:1: the same selection

    { modules { <module> { sensorValues { <fieldCamel> { <leafCamel> {
        value timestamp } } } } } }

must return equal data from both services. The fields and leaves come from the
contract (``tests.graphql.resolved``), which leaves out what thrs-api does not
serve (a field shadowed by a same-named camelCase sibling).

Computed/controller fields are relayed from what the control loop publishes to
``{controller_prefix}/<module>/<field>``; this harness publishes only raw
sensor topics and runs no control loop, so their parity is skipped here (the
UI-driven suite with a lockstep run is the place for it) while the thrs-api
side of the shape is still asserted.

Each service reads its own prefixes (``stack_config``); every model is
published under both.

Run from ``zero-thrs-control/`` with the stack up::

    uv run pytest tests/graphql/test_cross_api_parity_exhaustive.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pytest
from aiomqtt import Client as MqttClient

from tests.graphql.parity import (
    query_data,
    seed_distinct_values,
    values_equal,
)
from tests.graphql.resolved import ResolvedSpec, section_of
from tests.graphql.stack_config import (
    MQTT_GRAPHQL_URL,
    MQTT_HOST,
    MQTT_PORT,
    THRS_API_URL,
    mqtt_graphql_config,
    thrs_api_config,
)
from thrs.input_output.base import ThrsValues
from thrs.orchestration.comms import PartialMqttMapping, device_module_prefix
from thrs.spec.asyncapi import all_module_descriptions

pytestmark = pytest.mark.migration

PUBLISH_PREFIXES = sorted(
    {
        thrs_api_config().mqtt_devices_topic_prefix,
        mqtt_graphql_config().mqtt_devices_topic_prefix,
    }
)

CONTRACT = ResolvedSpec(thrs_api_config())


@dataclass(frozen=True)
class FieldCase:
    """One sensor field of one module, with the leaves to compare."""

    module: str
    gql_field: str
    leaves: tuple[str, ...]
    computed: bool


def _all_field_cases() -> list[FieldCase]:
    return [
        FieldCase(
            module=module,
            gql_field=field["gql"],
            leaves=tuple(leaf["gql"] for leaf in field["leaves"]),
            computed=field["computed"],
        )
        for module, member in sorted(CONTRACT.members.items())
        for field in section_of(member, "sensorValues")["fields"]
    ]


ALL_FIELD_CASES: list[FieldCase] = _all_field_cases()
MODULES: list[str] = sorted({case.module for case in ALL_FIELD_CASES})


# --- Model building / publishing -------------------------------------------


def _build_model(sensor_cls: type[ThrsValues]) -> ThrsValues:
    model = sensor_cls.zero()
    seed_distinct_values(model)
    return model


async def _publish_module(
    mqtt_client: MqttClient, module: str, model: ThrsValues
) -> None:
    """Publish every raw per-field topic of a module's model to both prefixes,
    using the production splitter (same as the control service)."""
    module_prefix = device_module_prefix(module)
    for prefix in PUBLISH_PREFIXES:
        mapping = PartialMqttMapping(type(model), prefix, module_prefix)
        for topic, payload in mapping.split_to_topics(model).items():
            await mqtt_client.publish(topic, payload=payload, retain=True)


def _module_query(module: str, cases: list[FieldCase]) -> str:
    """The `<fieldCamel> { <leafCamel> { value timestamp } ... }` selection
    shared by both APIs (the 1:1 selection)."""
    body = "\n".join(
        f"{case.gql_field} {{ "
        + " ".join(f"{leaf} {{ value timestamp }}" for leaf in case.leaves)
        + " }"
        for case in cases
    )
    return f"{{ modules {{ {module} {{ sensorValues {{ {body} }} }} }} }}"


# --- Fixtures ---------------------------------------------------------------


@pytest.fixture(scope="session")
def published_models(docker_stack: None) -> dict[str, ThrsValues]:
    """Publish one complete valid model per module once, and return the models
    (their seeded values are the parity baseline). thrs-api's ``sensorValues``
    only goes non-null once the whole model validates, so each module needs a
    complete publish."""
    models = {
        module: _build_model(description.sensor_values_cls)
        for module, description in all_module_descriptions().items()
    }

    async def _publish_all() -> None:
        async with MqttClient(MQTT_HOST, MQTT_PORT) as mqtt_client:
            for module, model in models.items():
                await _publish_module(mqtt_client, module, model)
            # Let both services' subscribers receive and cache the retained
            # messages before any query runs.
            await asyncio.sleep(3.0)

    asyncio.run(_publish_all())
    return models


# --- Tests ------------------------------------------------------------------


@pytest.mark.parametrize("module", MODULES)
def test_thrs_api_exposes_full_sensor_shape(
    module: str, published_models: dict[str, ThrsValues]
) -> None:
    """Contract check (thrs-api side): every raw field the contract declares
    is present and non-null under ``modules.<module>.sensorValues`` once the
    complete model is published. This is what mqtt-graphql must match 1:1."""
    raw_cases = [c for c in ALL_FIELD_CASES if c.module == module and not c.computed]
    data = query_data(THRS_API_URL, _module_query(module, raw_cases))
    sensor_values = data["modules"][module]["sensorValues"]
    assert sensor_values is not None, (
        f"thrs-api {module}.sensorValues is null: the full model did not "
        f"validate; did every per-field topic publish?"
    )
    for case in raw_cases:
        component = sensor_values[case.gql_field]
        assert component is not None, f"{module}.{case.gql_field} missing on thrs-api"
        for leaf in case.leaves:
            assert leaf in component, (
                f"{module}.{case.gql_field}.{leaf} missing on thrs-api"
            )


@pytest.mark.parametrize(
    "case",
    [c for c in ALL_FIELD_CASES if not c.computed],
    ids=lambda c: f"{c.module}.{c.gql_field}",
)
def test_raw_field_parity(
    case: FieldCase, published_models: dict[str, ThrsValues]
) -> None:
    """Exhaustive 1:1 read parity for one raw sensor field: thrs-api and
    mqtt-graphql must return equal ``{value, timestamp}`` for every leaf."""
    query = _module_query(case.module, [case])
    thrs_api = query_data(THRS_API_URL, query)["modules"][case.module]["sensorValues"]
    mqtt_graphql = query_data(MQTT_GRAPHQL_URL, query)["modules"][case.module][
        "sensorValues"
    ]

    assert thrs_api is not None, f"thrs-api {case.module}.sensorValues null"
    assert mqtt_graphql is not None, f"mqtt-graphql {case.module}.sensorValues null"

    thrs_component = thrs_api[case.gql_field]
    mqtt_component = mqtt_graphql[case.gql_field]
    for leaf in case.leaves:
        assert values_equal(thrs_component[leaf], mqtt_component[leaf]), (
            f"{case.module}.{case.gql_field}.{leaf}: "
            f"thrs-api={thrs_component[leaf]!r} mqtt-graphql={mqtt_component[leaf]!r}"
        )


@pytest.mark.parametrize(
    "case",
    [c for c in ALL_FIELD_CASES if c.computed],
    ids=lambda c: f"{c.module}.{c.gql_field}",
)
def test_computed_field_parity(case: FieldCase) -> None:
    """Computed/controller fields are relayed from what the control loop
    publishes; this harness runs no control loop, so nothing is published for
    either service to serve. See the module docstring."""
    pytest.skip(
        f"computed field {case.module}.{case.gql_field} is relayed from a "
        "controller topic this harness never publishes"
    )
