"""Power-tags topic loader using annotated offset-model."""

import json
import os
import re
from functools import partial
from pathlib import Path
from typing import Annotated, Any, Literal

from faststream.mqtt import MQTTBroker, QoS
from faststream.specification import AsyncAPI
from pydantic import BaseModel, Field
from zero_modbus_bridge.bit_ops import is_finite_float
from zero_modbus_bridge.io import AnnotationModbusTopic, ModbusField, ModbusTopic
from zero_modbus_bridge.publisher import (
    ParametrizedMQTTPublisher,
    finalize_parametrized_spec,
)

TOPIC_PREFIX = "power-tags"
TOPIC_PATTERN = f"{TOPIC_PREFIX}/{{panel}}/{{slug}}"


class PowerTag(BaseModel):
    """One PowerTag breaker's readings.

    The annotated ``ModbusField(register=…)`` addresses are absolute: every
    breaker exposes the same register block on its own Modbus slave id, so
    this model is the single source of truth for the register map.
    """

    component: str | None = None
    panel: str | None = None
    consumer: str | None = None
    current_a: Annotated[
        float | None,
        ModbusField(register=3000, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "A"}),
    ]
    current_b: Annotated[
        float | None,
        ModbusField(register=3002, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "A"}),
    ]
    current_c: Annotated[
        float | None,
        ModbusField(register=3004, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "A"}),
    ]
    current_n: Annotated[
        float | None,
        ModbusField(register=3006, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "A"}),
    ]
    voltage_an: Annotated[
        float | None,
        ModbusField(register=3028, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "V"}),
    ]
    voltage_bn: Annotated[
        float | None,
        ModbusField(register=3030, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "V"}),
    ]
    voltage_cn: Annotated[
        float | None,
        ModbusField(register=3032, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "V"}),
    ]
    active_power_a: Annotated[
        float | None,
        ModbusField(register=3054, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "W"}),
    ]
    active_power_b: Annotated[
        float | None,
        ModbusField(register=3056, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "W"}),
    ]
    active_power_c: Annotated[
        float | None,
        ModbusField(register=3058, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "W"}),
    ]
    active_power_total: Annotated[
        float | None,
        ModbusField(register=3060, data_type="float32", validator=is_finite_float),
        Field(json_schema_extra={"x-unit": "W"}),
    ]
    power_factor_a: Annotated[
        float | None,
        ModbusField(register=3078, data_type="float32", validator=is_finite_float),
    ]
    power_factor_b: Annotated[
        float | None,
        ModbusField(register=3080, data_type="float32", validator=is_finite_float),
    ]
    power_factor_c: Annotated[
        float | None,
        ModbusField(register=3082, data_type="float32", validator=is_finite_float),
    ]
    power_factor_total: Annotated[
        float | None,
        ModbusField(register=3084, data_type="float32", validator=is_finite_float),
    ]


def _bridges_path() -> str:
    return os.environ.get(
        "MODBUS_BRIDGES_PATH",
        str(Path(__file__).parent / "../../modbus_bridges.json"),
    )


def _read_bridges() -> list[dict[str, Any]]:
    with open(_bridges_path(), "r", encoding="utf-8") as f:
        return json.load(f)


class BridgeSpec(BaseModel):
    """One physical Modbus TCP gateway and the topics served behind it.

    Every entry in modbus_bridges.json describes a single gateway; its
    address is environment-specific and resolved via `modbus_host_env` /
    `modbus_port_env` rather than stored in the (generated) JSON. Each topic
    carries its own `unit_id`: one Modbus slave per breaker.
    """

    panel: str
    topics: list[ModbusTopic]


def modbus_env(panel: str, field: Literal["HOST", "PORT"]) -> str:
    """Env var name carrying the gateway host for a panel (`10P0.1` → `MODBUS_HOST_10P0_1`)."""
    suffix = re.sub(r"[^A-Z0-9]+", "_", panel.upper()).strip("_")
    return f"MODBUS_{field}_{suffix}"


modbus_host_env = partial(modbus_env, field="HOST")
modbus_port_env = partial(modbus_env, field="PORT")


def build_topic(panel: str, name: str) -> str:
    """Full MQTT topic for a breaker: `power-tags/{panel}/{name}`."""
    return f"{TOPIC_PREFIX}/{panel}/{name}"


def read_modbus_bridge_specs() -> list[BridgeSpec]:
    """Group the bridges JSON per gateway instead of flattening all topics."""
    return [
        BridgeSpec(
            panel=unit["panel"],
            topics=[parse_topic(t, unit["panel"]) for t in unit["topics"]],
        )
        for unit in _read_bridges()
    ]


def _extra_fields(topic_raw: dict) -> dict[str, Any]:
    raw = topic_raw.get("extra_fields", {})
    if isinstance(raw, list):
        return {ef["field_name"]: ef["value"] for ef in raw}
    return raw


def parse_topic(t: dict, panel: str) -> ModbusTopic:
    """Build a ModbusTopic from a JSON topic entry; each breaker is its own slave.

    The register layout (absolute addresses) and engineering units are carried
    by the PowerTag model, so the JSON only contributes the topic's identity
    and slave id.
    """
    return AnnotationModbusTopic(
        topic=build_topic(panel, t["name"]),
        model=PowerTag,
        unit_id=t["unit_id"],
        extra_fields=_extra_fields(t),
    )


def read_topics_metadata() -> dict[str, Any]:
    """Build the generic topic-metadata document consumed by zero-mqtt-graphql.

    One entry per breaker: the concrete MQTT topic plus static attributes.
    Panel/slug mirror the topic segments; component/consumer carry the
    human-readable identity from the Excel sources and patches.
    """
    raw = _read_bridges()

    entries = [
        _metadata_entry(unit["panel"], topic_raw)
        for unit in raw
        for topic_raw in unit["topics"]
    ]
    group = entries[0]["topic"].split("/")[0] if entries else TOPIC_PREFIX
    return {"group": group, "group_by": "panel", "topics": entries}


def _metadata_entry(panel: str, topic_raw: dict) -> dict[str, Any]:
    extras = _extra_fields(topic_raw)
    return {
        "topic": build_topic(panel, topic_raw["name"]),
        "metadata": {
            "panel": extras.get("panel") or panel,
            "slug": topic_raw["name"],
            "component": extras.get("component"),
            "consumer": extras.get("consumer"),
        },
    }


def topic_parameters(specs: list[BridgeSpec]) -> dict[str, dict[str, Any]]:
    """AsyncAPI channel parameters (enums) collected from the bridge specs."""
    panels = sorted({spec.panel for spec in specs})
    slugs = sorted(
        {topic.topic.rsplit("/", 1)[-1] for spec in specs for topic in spec.topics}
    )
    return {
        "panel": {"description": "Electrical panel identifier.", "enum": panels},
        "slug": {"description": "Dashified consumer name.", "enum": slugs},
    }


def create_publisher(
    broker: MQTTBroker, specs: list[BridgeSpec]
) -> ParametrizedMQTTPublisher:
    """Register the parametrized publisher for the whole topic family.

    Single registration point: runtime publishing (run) and spec generation
    (print-asyncapi) must describe exactly the same publisher.
    """
    return ParametrizedMQTTPublisher.create(
        broker,
        TOPIC_PATTERN,
        parameters=topic_parameters(specs),
        description="Electrical measurements for every PowerTag breaker.",
        qos=QoS.AT_LEAST_ONCE,
        schema=PowerTag,
    )


def build_asyncapi(title: str = "Power Tags", version: str = "1.0.0") -> dict[str, Any]:
    """AsyncAPI 3.0 document generated by FastStream.

    A single parametrized channel describes the whole topic family
    (`power-tags/{panel}/{slug}`); the concrete option space is documented
    as parameter enums collected from modbus_bridges.json.
    """
    specs = read_modbus_bridge_specs()
    broker = MQTTBroker("localhost:1883")
    publisher = create_publisher(broker, specs)
    doc = (
        AsyncAPI(broker, title=title, version=version).to_specification().to_jsonable()
    )
    return finalize_parametrized_spec(doc, publisher.parameters)
