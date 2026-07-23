"""Power-tags topic loader using annotated offset-model."""

import json
import os
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel
from zero_modbus_bridge.io import ModbusField, ModbusTopic


class PowerTag(BaseModel):
    """Single PowerTag breaker — fields relative to `start_register`."""

    current_a: Annotated[
        float | None, ModbusField(offset=0, count=2, data_type="float32")
    ]
    current_b: Annotated[
        float | None, ModbusField(offset=2, count=2, data_type="float32")
    ]
    current_c: Annotated[
        float | None, ModbusField(offset=4, count=2, data_type="float32")
    ]
    current_n: Annotated[
        float | None, ModbusField(offset=6, count=2, data_type="float32")
    ]
    voltage_an: Annotated[
        float | None, ModbusField(offset=28, count=2, data_type="float32")
    ]
    voltage_bn: Annotated[
        float | None, ModbusField(offset=30, count=2, data_type="float32")
    ]
    voltage_cn: Annotated[
        float | None, ModbusField(offset=32, count=2, data_type="float32")
    ]
    active_power_a: Annotated[
        float | None, ModbusField(offset=54, count=2, data_type="float32")
    ]
    active_power_b: Annotated[
        float | None, ModbusField(offset=56, count=2, data_type="float32")
    ]
    active_power_c: Annotated[
        float | None, ModbusField(offset=58, count=2, data_type="float32")
    ]
    active_power_total: Annotated[
        float | None, ModbusField(offset=60, count=2, data_type="float32")
    ]
    power_factor_a: Annotated[
        float | None, ModbusField(offset=78, count=2, data_type="float32")
    ]
    power_factor_b: Annotated[
        float | None, ModbusField(offset=80, count=2, data_type="float32")
    ]
    power_factor_c: Annotated[
        float | None, ModbusField(offset=82, count=2, data_type="float32")
    ]
    power_factor_total: Annotated[
        float | None, ModbusField(offset=84, count=2, data_type="float32")
    ]


def parse_topic(t: dict, unit_id: int) -> ModbusTopic:
    """Build a ModbusTopic from a JSON bridge entry."""
    first_reg = t["modbus_fields"][0]["modbus_register"]
    extra_fields_raw = t.get("extra_fields", {})
    if isinstance(extra_fields_raw, list):
        extra_fields = {ef["field_name"]: ef["value"] for ef in extra_fields_raw}
    else:
        extra_fields = extra_fields_raw
    return ModbusTopic(
        topic=t["topic"],
        model=PowerTag,
        start_register=first_reg,
        unit_id=unit_id,
        extra_fields=extra_fields,
    )


def read_modbus_topics() -> list[ModbusTopic]:
    json_path = os.environ.get(
        "MODBUS_BRIDGES_PATH",
        str(Path(__file__).parent / "../../modbus_bridges.json"),
    )
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return [parse_topic(t, unit["unit_id"]) for unit in raw for t in unit["topics"]]
