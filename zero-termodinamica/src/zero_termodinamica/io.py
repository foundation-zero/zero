import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, TypeAdapter


class LiteralField(BaseModel):
    field_name: str
    value: Any


class Address(BaseModel):
    modbus_register: int
    field_name: str
    description: str | None = None
    scale_factor: float = 1


class MqttTopic(BaseModel):
    topic: str
    modbus_fields: list[Address]
    extra_fields: list[LiteralField] = []


class ModbusUnit(BaseModel):
    unit_id: int
    topics: list[MqttTopic]


def read_modbus_units() -> list[ModbusUnit]:
    json_path = Path(__file__).parent / "../../modbus_bridges.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return TypeAdapter(list[ModbusUnit]).validate_python(json.loads(f.read()))
