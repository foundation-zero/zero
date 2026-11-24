import json
import os
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel
from zero_modbus_bridge.io import AnnotationModbusTopic, ModbusField, ModbusTopic


class AirConditioningRoom(BaseModel):
    power: Annotated[int | None, ModbusField(offset=0)]
    setpoint_room_temperature: Annotated[
        float | None, ModbusField(offset=1, scale_factor=0.01)
    ]
    fan_speed: Annotated[int | None, ModbusField(offset=2)]
    air_temperature_in: Annotated[
        float | None, ModbusField(offset=3, scale_factor=0.01)
    ]
    status: Annotated[int | None, ModbusField(offset=4)]
    ahu_mode: Annotated[int | None, ModbusField(offset=5)]
    heater_power: Annotated[int | None, ModbusField(offset=6)]
    humidity: Annotated[int | None, ModbusField(offset=7)]
    reg_split: str | None = None
    room: str | None = None


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


class VentilationUnit(BaseModel):
    """One DVS air handler slot on a ventilation bridge (Fw 8.14.18 Custom DVS)."""

    air_flow: Annotated[int | None, ModbusField(offset=0)]
    setpoint_air_flow: Annotated[int | None, ModbusField(offset=1)]
    co2_level: Annotated[int | None, ModbusField(offset=2)]
    setpoint_co2: Annotated[int | None, ModbusField(offset=3)]
    humidity: Annotated[float | None, ModbusField(offset=4, scale_factor=0.1)]
    setpoint_humidity: Annotated[float | None, ModbusField(offset=5, scale_factor=0.1)]
    co2_level_2: Annotated[int | None, ModbusField(offset=6)]
    setpoint_co2_2: Annotated[int | None, ModbusField(offset=7)]
    humidity_2: Annotated[float | None, ModbusField(offset=8, scale_factor=0.1)]
    setpoint_humidity_2: Annotated[
        float | None, ModbusField(offset=9, scale_factor=0.1)
    ]
    errors: Annotated[int | None, ModbusField(offset=10)]
    bridge: str | None = None
    unit: str | None = None
    room: str | None = None


class HeatPump(BaseModel):
    """The HPB, wired to its own bridge as slave unit 2 of the base register map.

    The external water pump may only stop once ``compressor_speed`` reads zero.
    """

    system_disabled: Annotated[int | None, ModbusField(register=30)]
    compressor_speed: Annotated[
        float | None, ModbusField(register=140, scale_factor=0.1)
    ]
    water_pump_speed: Annotated[
        float | None, ModbusField(register=141, scale_factor=0.1)
    ]
    # The map says hundredths of W; live it reads 13 at 0.54 A, so tens of W.
    compressor_power: Annotated[
        float | None, ModbusField(register=182, scale_factor=10.0)
    ]
    compressor_current: Annotated[
        float | None, ModbusField(register=185, scale_factor=0.01)
    ]
    active_error: Annotated[int | None, ModbusField(register=190)]
    power: Annotated[int | None, ModbusField(register=210)]
    setpoint_temperature: Annotated[
        float | None, ModbusField(register=211, scale_factor=0.01)
    ]
    temperature: Annotated[float | None, ModbusField(register=213, scale_factor=0.01)]
    status: Annotated[int | None, ModbusField(register=214)]


class ColdRoom(BaseModel):
    """The fridge or freezer, each on its own bridge and slave slot of the base map.

    The slot fields are offsets from the topic's ``start_register``: 210 for the
    fridge (slot 2), 220 for the freezer (slot 3). Temperatures are signed: the
    freezer runs between -5 and -20 °C.
    """

    system_disabled: Annotated[int | None, ModbusField(register=30)]
    compressor_speed: Annotated[
        float | None, ModbusField(register=140, scale_factor=0.1)
    ]
    # The map says hundredths of W; live it reads 13 at 0.54 A, so tens of W.
    compressor_power: Annotated[
        float | None, ModbusField(register=182, scale_factor=10.0)
    ]
    compressor_current: Annotated[
        float | None, ModbusField(register=185, scale_factor=0.01)
    ]
    active_error: Annotated[int | None, ModbusField(register=190)]
    power: Annotated[int | None, ModbusField(offset=0)]
    setpoint_temperature: Annotated[
        float | None,
        ModbusField(offset=1, data_type="int16", scale_factor=0.01),
    ]
    temperature: Annotated[
        float | None,
        ModbusField(offset=3, data_type="int16", scale_factor=0.01),
    ]
    status: Annotated[int | None, ModbusField(offset=4)]


_MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    "air_conditioning_room": AirConditioningRoom,
    "ac_misc": ACMisc,
    "ventilation_unit": VentilationUnit,
    "heat_pump": HeatPump,
    "cold_room": ColdRoom,
}


def _parse_topic(t: dict, unit_id: int) -> ModbusTopic:
    """Build a ModbusTopic from a JSON bridge entry, validating model key."""
    model_key = t.get("model", "")
    if model_key not in _MODEL_REGISTRY:
        raise ValueError(
            f"Topic {t['topic']} has unknown model key "
            f"{model_key!r}; expected one of {sorted(_MODEL_REGISTRY)}"
        )
    start_register = t.get("start_register", t["modbus_fields"][0]["modbus_register"])
    extra_fields_raw = t.get("extra_fields", {})
    if isinstance(extra_fields_raw, list):
        extra_fields = {ef["field_name"]: ef["value"] for ef in extra_fields_raw}
    else:
        extra_fields = extra_fields_raw
    return AnnotationModbusTopic(
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
