import json
import os
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field
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
    # Relative humidity as a ratio (0..1); the register holds whole percents.
    humidity: Annotated[float | None, ModbusField(offset=7, scale_factor=0.01)]
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
    # Relative humidity as a ratio (0..1); the registers hold tenths of percents.
    humidity: Annotated[float | None, ModbusField(offset=4, scale_factor=0.001)]
    setpoint_humidity: Annotated[
        float | None, ModbusField(offset=5, scale_factor=0.001)
    ]
    co2_level_2: Annotated[int | None, ModbusField(offset=6)]
    setpoint_co2_2: Annotated[int | None, ModbusField(offset=7)]
    humidity_2: Annotated[float | None, ModbusField(offset=8, scale_factor=0.001)]
    setpoint_humidity_2: Annotated[
        float | None, ModbusField(offset=9, scale_factor=0.001)
    ]
    errors: Annotated[int | None, ModbusField(offset=10)]
    bridge: str | None = None
    unit: str | None = None
    room: str | None = None


def slave_block(slave: int) -> int:
    """First register of a slave's read-back block: 200 for slave 1, 210 for 2."""
    return 200 + 10 * (slave - 1)


class SlaveUnit(BaseModel):
    """A unit on its own bridge, as one slave of the base register map.

    Its slot fields are offsets from ``slave_block(slave)``; slot 1 (200..204)
    only holds placeholders on these bridges.
    """

    system_disabled: Annotated[
        int | None,
        ModbusField(register=30),
        Field(description="Global on/off: 1=off, 0=on"),
    ]
    compressor_speed: Annotated[
        float | None,
        ModbusField(register=140, scale_factor=0.1),
        Field(description="Inverter compressor speed (%)"),
    ]
    # The register says 0.01 W; from the data we assume 0.01 kW, i.e. 10 W.
    compressor_power: Annotated[
        float | None,
        ModbusField(register=182, scale_factor=10.0),
        Field(description="Compressor power (W)"),
    ]
    compressor_current: Annotated[
        float | None,
        ModbusField(register=185, scale_factor=0.01),
        Field(description="Compressor current (A)"),
    ]
    active_error: Annotated[
        int | None,
        ModbusField(register=190),
        Field(description="General active error bit field"),
    ]
    power: Annotated[
        int | None, ModbusField(offset=0), Field(description="Unit on/off: 0=off, 1=on")
    ]
    status: Annotated[
        int | None,
        ModbusField(offset=4),
        Field(description="Communication status bit field"),
    ]
    slave: int | None = None


class HeatPump(SlaveUnit):
    """The HPB. The external water pump may only stop once ``compressor_speed``
    reads zero."""

    water_pump_speed: Annotated[
        float | None,
        ModbusField(register=141, scale_factor=0.1),
        Field(description="Inverter water pump speed (%)"),
    ]
    setpoint_temperature: Annotated[
        float | None,
        ModbusField(offset=1, scale_factor=0.01),
        Field(description="Water set point (°C), 6..70"),
    ]
    temperature: Annotated[
        float | None,
        ModbusField(offset=3, scale_factor=0.01),
        Field(description="Water temperature (°C)"),
    ]


class ColdRoom(SlaveUnit):
    """The fridge or freezer. Temperatures are signed (two's complement): the
    fridge runs at 1..20 °C, the freezer at -5..-20 °C."""

    setpoint_temperature: Annotated[
        float | None,
        ModbusField(offset=1, data_type="int16", scale_factor=0.01),
        Field(description="Set point (°C)"),
    ]
    temperature: Annotated[
        float | None,
        ModbusField(offset=3, data_type="int16", scale_factor=0.01),
        Field(description="Cold room temperature (°C)"),
    ]


MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    "air_conditioning_room": AirConditioningRoom,
    "ac_misc": ACMisc,
    "ventilation_unit": VentilationUnit,
    "heat_pump": HeatPump,
    "cold_room": ColdRoom,
}


def _parse_topic(t: dict, unit_id: int) -> ModbusTopic:
    """Build a ModbusTopic from a JSON bridge entry, validating model key."""
    model_key = t.get("model", "")
    if model_key not in MODEL_REGISTRY:
        raise ValueError(
            f"Topic {t['topic']} has unknown model key "
            f"{model_key!r}; expected one of {sorted(MODEL_REGISTRY)}"
        )
    extra_fields_raw = t.get("extra_fields", {})
    if isinstance(extra_fields_raw, list):
        extra_fields = {ef["field_name"]: ef["value"] for ef in extra_fields_raw}
    else:
        extra_fields = extra_fields_raw
    if (slave := extra_fields.get("slave")) is not None:
        start_register = slave_block(slave)
    else:
        start_register = t["modbus_fields"][0]["modbus_register"]
    return AnnotationModbusTopic(
        topic=t["topic"],
        model=MODEL_REGISTRY[model_key],
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
