import json
from pathlib import Path
from typing import Any, List

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
    modbus_fields: List[Address]
    extra_fields: List[LiteralField] = []


class ModbusUnit(BaseModel):
    unit_id: int
    topics: List[MqttTopic]


def read_modbus_units() -> List[ModbusUnit]:
    json_path = Path(__file__).parent / "../../modbus_bridges.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return TypeAdapter(list[ModbusUnit]).validate_python(json.loads(f.read()))
