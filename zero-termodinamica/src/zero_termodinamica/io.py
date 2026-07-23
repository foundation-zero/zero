import json
import os
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel
from zero_modbus_bridge.io import ModbusField, ModbusTopic


class AirConditioningRoom(BaseModel):
    power: Annotated[int | None, ModbusField(offset=0)]
    setpoint_room_temperature: Annotated[int | None, ModbusField(offset=1)]
    fan_speed: Annotated[int | None, ModbusField(offset=2)]
    air_temperature_in: Annotated[int | None, ModbusField(offset=3)]
    status: Annotated[int | None, ModbusField(offset=4)]
    ahu_mode: Annotated[int | None, ModbusField(offset=5)]
    heater_power: Annotated[int | None, ModbusField(offset=6)]
    humidity: Annotated[int | None, ModbusField(offset=7)]


class ACMisc(BaseModel):
    engine_box_compressor_speed: Annotated[int | None, ModbusField(register=140)]
    engine_box_water_pump_speed: Annotated[
        float | None, ModbusField(register=141, scale_factor=0.01)
    ]
    current_req_pressure: Annotated[
        float | None, ModbusField(register=142, scale_factor=0.001)
    ]
    engine_box_t_sea_water: Annotated[
        float | None, ModbusField(register=145, scale_factor=0.01)
    ]
    engine_box_p_gas: Annotated[
        float | None, ModbusField(register=149, scale_factor=0.001)
    ]
    engine_box_p_liquid: Annotated[
        float | None, ModbusField(register=150, scale_factor=0.001)
    ]
    engine_box_p_condenser: Annotated[
        float | None, ModbusField(register=151, scale_factor=0.001)
    ]
    engine_box_compressor2_speed: Annotated[int | None, ModbusField(register=155)]
    watt_ac_compressor_1: Annotated[
        float | None, ModbusField(register=182, scale_factor=0.01)
    ]
    watt_ac_compressor_2: Annotated[
        float | None, ModbusField(register=183, scale_factor=0.01)
    ]
    watt_sea_water_pump: Annotated[
        float | None, ModbusField(register=184, scale_factor=0.01)
    ]
    ac_compressor_1: Annotated[
        float | None, ModbusField(register=185, scale_factor=0.01)
    ]
    ac_compressor_2: Annotated[
        float | None, ModbusField(register=186, scale_factor=0.01)
    ]
    sea_water_pump: Annotated[
        float | None, ModbusField(register=187, scale_factor=0.01)
    ]


_MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    "air_conditioning_room": AirConditioningRoom,
    "ac_misc": ACMisc,
}


def _parse_topic(t: dict, unit_id: int) -> ModbusTopic:
    """Build a ModbusTopic from a JSON bridge entry, validating model key."""
    model_key = t.get("model", "")
    if model_key not in _MODEL_REGISTRY:
        raise ValueError(
            f"Topic {t['topic']} has unknown model key "
            f"{model_key!r}; expected one of {sorted(_MODEL_REGISTRY)}"
        )
    start_register = t["modbus_fields"][0]["modbus_register"]
    extra_fields_raw = t.get("extra_fields", {})
    if isinstance(extra_fields_raw, list):
        extra_fields = {ef["field_name"]: ef["value"] for ef in extra_fields_raw}
    else:
        extra_fields = extra_fields_raw
    return ModbusTopic(
        topic=t["topic"],
        model=_MODEL_REGISTRY[model_key],
        start_register=start_register,
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

    return [_parse_topic(t, unit["unit_id"]) for unit in raw for t in unit["topics"]]
