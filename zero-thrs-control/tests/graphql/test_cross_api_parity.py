"""Checks that the Rust ``mqtt-graphql`` service (5103) returns the same data as
the Python ``thrs-api`` service (5102) for the THRS ``thrusters`` module.

Read-only end-to-end: publish a full known ``ThrustersSensorValues`` payload to
MQTT, wait for both services to pick it up, then query each GraphQL API and
assert they agree with each other and with the published values. Mutations are
out of scope (mqtt-graphql doesn't have them yet).

Two differences between the services shape the test, both found against the
running stack:

1. thrs-api's ``sensorValues`` is all-or-nothing. ``PartialModelBuilder``
   accumulates per-field messages and only goes non-null once the whole
   ``ThrustersSensorValues`` model validates (all ~19 fields). mqtt-graphql is
   row-based: each field is queryable on its own. So to compare even one field
   we publish a complete model, built from ``ThrustersSensorValues.zero()`` with
   known values and split per-topic via ``PartialMqttMapping.split_to_topics``,
   same as the real control service.

2. mqtt-graphql's group ``values`` use lowercase field names (``naming.rs``
   lowercases every token, ``PositionRel`` -> ``positionrel``); thrs-api emits
   camelCase. Single-word fields match, multi-word ones don't, so the comparison
   is casing-tolerant: it matches the ``{value, timestamp}`` leaves per field and
   compares timestamps as instants (thrs-api serializes ``+00:00``, the wire
   payload carries ``Z``).

Not covered: computed/controller fields. thrs-api derives those in pydantic;
mqtt-graphql only relays whatever lands on ``thrs/controller/thrusters/*``.
Making them agree would mean duplicating thrs-api's formulae, so this sticks to
the raw sensor fields, where real device data flows.

Prefix caveat: in the running stack thrs-api uses ``devices_topic`` /
``controller_topic`` (docker-compose env) while mqtt-graphql's specs use the
default ``simulation`` prefix, so neither service sees the other's values. That's
a real bug on its own (placeholder prefixes never reconciled with the spec). To
still get a parity check we publish to both prefixes;
``test_thrs_api_and_mqtt_graphql_prefixes_currently_differ`` fails loudly once
someone unifies them, which is the cue to publish just once.

Run with the docker-compose stack up, or let the ``docker_stack`` fixture start
it::

    docker compose --profile thrs --profile data up -d --wait \\
        vernemq postgres thrs-api mqtt-graphql
    pytest zero-thrs-control/tests/graphql/test_cross_api_parity.py

Run from ``zero-thrs-control/`` with ``uv run pytest`` so its ``thrs`` package
and ``aiomqtt`` / ``httpx`` deps are available.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pytest
from aiomqtt import Client as MqttClient

from thrs.input_output.modules.thrusters import ThrustersSensorValues
from thrs.orchestration.comms import PartialMqttMapping

REPO_ROOT = Path(__file__).resolve().parents[3]

MQTT_HOST = "localhost"
MQTT_PORT = 1883

THRS_API_URL = "http://localhost:5102/graphql"
MQTT_GRAPHQL_URL = "http://localhost:5103/graphql"

# See the module docstring's prefix caveat: these differ in the running stack
# (docker-compose env vs. the specs' default), so we publish to both.
THRS_API_DEVICES_PREFIX = "devices_topic"
THRS_API_CONTROLLER_PREFIX = "controller_topic"
MQTT_GRAPHQL_DEVICES_PREFIX = "simulation"
MQTT_GRAPHQL_CONTROLLER_PREFIX = "thrs/controller"

# The module prefix baked into every thrusters topic (see
# ``ModuleMqttMapping`` / ``ControlApiChannels`` in ``thrs.orchestration.comms``).
MODULE_PREFIX = "500000-thrs/thrusters"


@dataclass(frozen=True)
class Leaf:
    """One ``{value, timestamp}`` leaf compared between the two APIs."""

    model_attr: str
    """Attribute on the component holding the ``Stamped`` value, e.g.
    ``"temperature"`` on a ``TemperatureSensor`` or ``"position_rel"`` on a
    ``Valve``."""
    thrs_api_key: str
    """GraphQL subfield on thrs-api (Strawberry, camelCase)."""
    mqtt_graphql_key: str
    """GraphQL subfield on mqtt-graphql (lowercased by ``naming.rs``)."""
    value: float
    """Distinct known value published for this leaf."""


@dataclass(frozen=True)
class SensorCase:
    """One raw thrusters sensor field, read from the group row on mqtt-graphql
    and from ``sensorValues`` on thrs-api."""

    name: str
    model_field: str
    """Attribute on ``ThrustersSensorValues``, e.g. ``thrusters_flow_aft``."""
    thrs_api_field: str
    """GraphQL field under ``modules.thrusters.sensorValues`` (camelCase)."""
    topic_segment: str
    """Trailing topic segment identifying the mqtt-graphql group row, e.g.
    ``thrusters-flow-aft`` (matches ``hyphenize(model_field)``)."""
    leaves: tuple[Leaf, ...]


SENSOR_CASES: tuple[SensorCase, ...] = (
    SensorCase(
        name="thrusters_temperature_aft",
        model_field="thrusters_temperature_aft",
        thrs_api_field="thrustersTemperatureAft",
        topic_segment="thrusters-temperature-aft",
        leaves=(Leaf("temperature", "temperature", "temperature", 42.5),),
    ),
    SensorCase(
        name="thrusters_flow_aft",
        model_field="thrusters_flow_aft",
        thrs_api_field="thrustersFlowAft",
        topic_segment="thrusters-flow-aft",
        leaves=(
            Leaf("flow", "flow", "flow", 3.2),
            Leaf("temperature", "temperature", "temperature", 41.0),
            Leaf("quantity", "quantity", "quantity", 101.4),
        ),
    ),
    SensorCase(
        name="thrusters_flowcontrol_aft",
        model_field="thrusters_flowcontrol_aft",
        thrs_api_field="thrustersFlowcontrolAft",
        topic_segment="thrusters-flowcontrol-aft",
        leaves=(
            # PositionRel is a Ratio validated 0..1 (see sensor.Valve).
            Leaf("position_rel", "positionRel", "positionrel", 0.75),
            Leaf("position_abs", "positionAbs", "positionabs", 270.0),
        ),
    ),
)

@dataclass(frozen=True)
class OutOfBoundsCase:
    """A raw sensor leaf pushed past its bound. Both APIs must reject the update
    and keep the last valid value: thrs-api because the whole
    ``ThrustersSensorValues`` model then fails re-validation, mqtt-graphql
    because strict validation drops the invalid payload for that topic (checked
    against its own ``x-field-schema``, not the group-wide ``anyOf`` union that
    would let it through)."""

    name: str
    sensor: SensorCase
    """The row whose complete valid payload is published first as the baseline."""
    leaf: Leaf
    """The leaf driven out of bounds; its ``value`` is the valid baseline both
    APIs must retain."""
    invalid_value: float
    bound: str
    """Human-readable bound, for assertion messages."""


# One bound backed by a pydantic ``Field(ge=...)`` (which pydantic emits as a
# JSON-Schema ``minimum``, so mqtt-graphql sees it too). Ratio bounds are
# deliberately excluded: ``Ratio`` uses an ``AfterValidator`` rather than
# ``Field``, so pydantic emits no ``minimum``/``maximum`` and the two APIs would
# genuinely disagree (thrs-api rejects, mqtt-graphql cannot).
OUT_OF_BOUNDS_CASES: tuple[OutOfBoundsCase, ...] = (
    OutOfBoundsCase(
        name="temperature_below_absolute_zero",
        sensor=SENSOR_CASES[0],  # thrusters_temperature_aft
        leaf=SENSOR_CASES[0].leaves[0],  # temperature, valid 42.5
        invalid_value=-300.0,  # < -273.15 (Celsius = Field(ge=-273.15))
        bound=">= -273.15 degC",
    ),
    OutOfBoundsCase(
        name="quantity_negative",
        sensor=SENSOR_CASES[1],  # thrusters_flow_aft
        leaf=SENSOR_CASES[1].leaves[2],  # quantity, valid 101.4
        invalid_value=-5.0,  # < 0 (Liter = Field(ge=0))
        bound=">= 0 L",
    ),
)


# The boolean ``Thruster.active`` field is published to a ``topic_override``
# (``dummy-pcs/thruster-aft-active``), so it has no module prefix and is a
# concrete (non-group) query on mqtt-graphql.
THRUSTER_AFT_ACTIVE_VALUE = True


def _mqtt_graphql_sensor_topic(segment: str) -> str:
    return f"{MQTT_GRAPHQL_DEVICES_PREFIX}/{MODULE_PREFIX}/{segment}"


def _build_model() -> ThrustersSensorValues:
    """A fully-valid ``ThrustersSensorValues`` with distinct known values on the
    fields under test (so parity is non-trivial and catches cross-wiring)."""
    model = ThrustersSensorValues.zero()
    for case in SENSOR_CASES:
        component = getattr(model, case.model_field)
        for leaf in case.leaves:
            getattr(component, leaf.model_attr).value = leaf.value
    model.thrusters_thruster_aft.active.value = THRUSTER_AFT_ACTIVE_VALUE
    return model


async def _publish_full_model(mqtt_client: MqttClient, model: ThrustersSensorValues) -> None:
    """Publish every per-field topic of ``model`` to both prefix variants, using
    the same production splitter the control service uses."""
    for prefix in (THRS_API_DEVICES_PREFIX, MQTT_GRAPHQL_DEVICES_PREFIX):
        mapping = PartialMqttMapping(ThrustersSensorValues, prefix, MODULE_PREFIX)
        for topic, payload in mapping.split_to_topics(model).items():
            await mqtt_client.publish(topic, payload=payload, retain=True)


def _docker_compose_available() -> bool:
    return shutil.which("docker") is not None


@pytest.fixture(scope="session")
def docker_stack() -> None:
    """Ensure vernemq, postgres, thrs-api and mqtt-graphql are up.

    If docker is unavailable in the current environment, the stack is assumed
    to already be running (e.g. started manually before invoking pytest) and
    this fixture is a no-op. Only these four services are waited on: grafana
    (profile ``data``) has a broken healthcheck (probes port 3001 but serves on
    3000) and would never become healthy, so it is deliberately not listed.
    """
    if not _docker_compose_available():
        return
    subprocess.run(
        ["docker", "compose", "--profile", "thrs", "--profile", "data", "up", "-d", "--wait",
         "vernemq", "postgres", "thrs-api", "mqtt-graphql"],
        cwd=REPO_ROOT,
        check=True,
        timeout=300,
    )


def _query_graphql(url: str, query: str) -> dict[str, Any]:
    response = httpx.post(url, json={"query": query}, timeout=10.0)
    response.raise_for_status()
    body = response.json()
    assert "errors" not in body, f"GraphQL errors from {url}: {body.get('errors')}"
    return body["data"]


def _thrs_api_query() -> str:
    fields = "\n".join(
        f"{case.thrs_api_field} {{ "
        + " ".join(f"{leaf.thrs_api_key} {{ value timestamp }}" for leaf in case.leaves)
        + " }"
        for case in SENSOR_CASES
    )
    return f"{{ modules {{ thrusters {{ sensorValues {{ {fields} }} }} }} }}"


def _mqtt_graphql_sensor_query() -> str:
    # One combined row list; each row carries all leaves, matched by topic.
    all_keys = {leaf.mqtt_graphql_key for case in SENSOR_CASES for leaf in case.leaves}
    values = " ".join(f"{key} {{ value timestamp }}" for key in sorted(all_keys))
    return f"{{ simulation500000ThrsThrusters {{ topic values {{ {values} }} }} }}"


def _parse_ts(raw: str | None) -> datetime | None:
    return datetime.fromisoformat(raw) if raw else None


def _assert_leaf_equal(name: str, thrs_api_leaf: dict[str, Any], mqtt_graphql_leaf: dict[str, Any],
                       published: float) -> None:
    assert thrs_api_leaf["value"] == published, (
        f"{name}: thrs-api value {thrs_api_leaf['value']!r} != published {published!r}"
    )
    assert mqtt_graphql_leaf["value"] == published, (
        f"{name}: mqtt-graphql value {mqtt_graphql_leaf['value']!r} != published {published!r}"
    )
    # Compare timestamps as instants: thrs-api serializes '+00:00', the wire
    # payload carries 'Z'. Same instant, different spelling.
    assert _parse_ts(thrs_api_leaf["timestamp"]) == _parse_ts(mqtt_graphql_leaf["timestamp"]), (
        f"{name}: timestamps differ: thrs-api={thrs_api_leaf['timestamp']!r} "
        f"mqtt-graphql={mqtt_graphql_leaf['timestamp']!r}"
    )


def test_thrs_api_and_mqtt_graphql_prefixes_currently_differ() -> None:
    """Documents the topic-prefix mismatch (see the module docstring's prefix
    caveat). Static, no broker; fails loudly once someone unifies the prefixes,
    the cue to simplify this test to a single publish."""
    assert THRS_API_DEVICES_PREFIX != MQTT_GRAPHQL_DEVICES_PREFIX
    assert THRS_API_CONTROLLER_PREFIX != MQTT_GRAPHQL_CONTROLLER_PREFIX


@pytest.mark.asyncio
async def test_thrs_api_and_mqtt_graphql_agree_on_raw_sensor_fields(docker_stack: None) -> None:
    """Publish one complete ``ThrustersSensorValues`` and assert both APIs
    return the same value/timestamp for each raw sensor field under test.

    A single full publish is required because thrs-api's ``sensorValues`` only
    becomes non-null once the whole model validates (see module docstring).
    """
    model = _build_model()
    async with MqttClient(MQTT_HOST, MQTT_PORT) as mqtt_client:
        await _publish_full_model(mqtt_client, model)
        # Give both services' MQTT subscribers time to receive and cache the
        # retained messages before querying their GraphQL APIs.
        await asyncio.sleep(2.0)

    thrs_api_data = _query_graphql(THRS_API_URL, _thrs_api_query())
    mqtt_graphql_data = _query_graphql(MQTT_GRAPHQL_URL, _mqtt_graphql_sensor_query())

    sensor_values = thrs_api_data["modules"]["thrusters"]["sensorValues"]
    assert sensor_values is not None, (
        "thrs-api sensorValues is null: the full ThrustersSensorValues model "
        "did not validate; did every per-field topic get published?"
    )

    rows = mqtt_graphql_data["simulation500000ThrsThrusters"]
    rows_by_topic = {row["topic"]: row["values"] for row in rows}

    for case in SENSOR_CASES:
        topic = _mqtt_graphql_sensor_topic(case.topic_segment)
        assert topic in rows_by_topic, (
            f"{case.name}: no row for topic {topic!r} in simulation500000ThrsThrusters "
            f"(is specs/thrs-thrusters-*-metadata.json up to date?) "
            f"Rows: {sorted(rows_by_topic)!r}"
        )
        thrs_api_component = sensor_values[case.thrs_api_field]
        mqtt_graphql_row = rows_by_topic[topic]
        for leaf in case.leaves:
            _assert_leaf_equal(
                f"{case.name}.{leaf.model_attr}",
                thrs_api_component[leaf.thrs_api_key],
                mqtt_graphql_row[leaf.mqtt_graphql_key],
                leaf.value,
            )


def _payload_with_invalid_leaf(
    topic_payload: str, valid_value: float, invalid_value: float
) -> str:
    """Replace the ``Value`` leaf equal to ``valid_value`` with ``invalid_value``
    in a per-topic wire payload (PascalCase-aliased ``{Value, TimeStamp}``). The
    model's known values are distinct, so the target leaf is unique within one
    topic's payload. Built by hand because the pydantic model rejects the
    out-of-bounds value on assignment (``validate_assignment``)."""
    data = json.loads(topic_payload)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "Value" and value == valid_value:
                    node[key] = invalid_value
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return json.dumps(data)


@pytest.mark.asyncio
async def test_thrs_api_and_mqtt_graphql_reject_out_of_bounds_sensor_values(
    docker_stack: None,
) -> None:
    """Publish one complete valid model, then drive individual raw sensor leaves
    past their bounds, and assert both APIs reject each out-of-bounds update and
    keep the previously cached valid value (see ``OutOfBoundsCase``). This is the
    validation half of parity: mqtt-graphql must reject the same values thrs-api
    does, which requires ``STRICT_VALIDATION`` on the mqtt-graphql service."""
    model = _build_model()
    async with MqttClient(MQTT_HOST, MQTT_PORT) as mqtt_client:
        await _publish_full_model(mqtt_client, model)
        await asyncio.sleep(2.0)
        # Now overwrite single leaves with out-of-bounds values on both prefixes.
        for case in OUT_OF_BOUNDS_CASES:
            for prefix in (THRS_API_DEVICES_PREFIX, MQTT_GRAPHQL_DEVICES_PREFIX):
                mapping = PartialMqttMapping(ThrustersSensorValues, prefix, MODULE_PREFIX)
                topics = mapping.split_to_topics(model)
                topic = next(
                    t for t in topics if t.endswith(f"/{case.sensor.topic_segment}")
                )
                bad_payload = _payload_with_invalid_leaf(
                    topics[topic], case.leaf.value, case.invalid_value
                )
                await mqtt_client.publish(topic, payload=bad_payload, retain=True)
        await asyncio.sleep(2.0)

    thrs_api_data = _query_graphql(THRS_API_URL, _thrs_api_query())
    mqtt_graphql_data = _query_graphql(MQTT_GRAPHQL_URL, _mqtt_graphql_sensor_query())

    sensor_values = thrs_api_data["modules"]["thrusters"]["sensorValues"]
    assert sensor_values is not None, (
        "thrs-api sensorValues is null: the valid baseline model did not validate"
    )
    rows_by_topic = {
        row["topic"]: row["values"]
        for row in mqtt_graphql_data["simulation500000ThrsThrusters"]
    }

    for case in OUT_OF_BOUNDS_CASES:
        thrs_api_leaf = sensor_values[case.sensor.thrs_api_field][case.leaf.thrs_api_key]
        assert thrs_api_leaf["value"] == case.leaf.value, (
            f"{case.name}: thrs-api accepted out-of-bounds {case.invalid_value} "
            f"(bound {case.bound}); expected it to reject and keep {case.leaf.value}"
        )
        topic = _mqtt_graphql_sensor_topic(case.sensor.topic_segment)
        mqtt_graphql_leaf = rows_by_topic[topic][case.leaf.mqtt_graphql_key]
        assert mqtt_graphql_leaf["value"] == case.leaf.value, (
            f"{case.name}: mqtt-graphql cached out-of-bounds {case.invalid_value} "
            f"(bound {case.bound}); expected strict validation to drop it and keep "
            f"{case.leaf.value}"
        )


# --- Thruster active-flag field (concrete, non-wildcard topic) ---

MQTT_GRAPHQL_THRUSTER_AFT_QUERY = """
{
    simulationDummyPcsThrusterAftActive {
        active { value timestamp }
    }
}
"""

THRS_API_THRUSTER_AFT_QUERY = """
{
    modules {
        thrusters {
            sensorValues {
                thrustersThrusterAft { active { value timestamp } }
            }
        }
    }
}
"""


@pytest.mark.asyncio
async def test_thrs_api_and_mqtt_graphql_agree_on_thruster_active(docker_stack: None) -> None:
    """Same idea for the boolean ``Thruster.active`` field, which lives on a
    ``topic_override`` (``dummy-pcs/thruster-aft-active``) and so is a concrete
    query on mqtt-graphql rather than a group row."""
    model = _build_model()
    async with MqttClient(MQTT_HOST, MQTT_PORT) as mqtt_client:
        await _publish_full_model(mqtt_client, model)
        await asyncio.sleep(2.0)

    thrs_api_data = _query_graphql(THRS_API_URL, THRS_API_THRUSTER_AFT_QUERY)
    mqtt_graphql_data = _query_graphql(MQTT_GRAPHQL_URL, MQTT_GRAPHQL_THRUSTER_AFT_QUERY)

    sensor_values = thrs_api_data["modules"]["thrusters"]["sensorValues"]
    assert sensor_values is not None
    thrs_api_active = sensor_values["thrustersThrusterAft"]["active"]["value"]
    mqtt_graphql_active = mqtt_graphql_data["simulationDummyPcsThrusterAftActive"]["active"][
        "value"
    ]

    assert thrs_api_active == THRUSTER_AFT_ACTIVE_VALUE
    assert mqtt_graphql_active == THRUSTER_AFT_ACTIVE_VALUE
    assert thrs_api_active == mqtt_graphql_active
