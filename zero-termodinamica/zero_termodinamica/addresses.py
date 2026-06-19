import json
from pathlib import Path
from typing import List

from pydantic import BaseModel, TypeAdapter


class Address(BaseModel):
    register: int
    field_name: str
    description: str | None = None
    scale_factor: float = 1


class MQTTTopic(BaseModel):
    topic: str
    fields: List[Address]


class ModbusUnit(BaseModel):
    unit_id: int
    topics: List[MQTTTopic]


def read_modbus_units() -> List[ModbusUnit]:
    json_path = Path(__file__).parent / "../modbus_units.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return TypeAdapter(list[ModbusUnit]).validate_python(json.loads(f.read()))


MODBUS_UNITS = read_modbus_units()
