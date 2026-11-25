"""Commands that MQTT clients (such as thrs) send to the Termodinamica bridges."""

import math
from functools import partial
from typing import Annotated, Any

from pydantic import BaseModel, Field
from zero_modbus_bridge.bit_ops import to_raw
from zero_modbus_bridge.commands import ModbusCommand
from zero_modbus_bridge.io import ModbusTopic, extract_modbus_fields
from zero_modbus_bridge.writer import RegisterWrite

from zero_termodinamica.io import HeatPump

HEAT_PUMP_TOPIC = "termodinamica/heat-pump"

# Base register map (docs/BridgeExchangeDataAddressMap_Rev Fw 8.14.17 - Base.pdf).
REG_DIAG_SPLIT_WRITE_SELECTION = 10
REG_DIAG_SPLIT_WRITE_PWR = 11
REG_DIAG_SPLIT_WRITE_SP_ROOM = 12
REG_SYSTEM_DISABLE = 30

# Writes take the scale the set point is read back with.
_SETPOINT_FIELD = extract_modbus_fields(HeatPump)["setpoint_temperature"]


class HeatPumpSet(BaseModel):
    """Switch the heat pump and set its water temperature.

    Whoever sends this runs the external water pump: it may only stop once
    ``compressor_speed`` on ``termodinamica/heat-pump`` reads zero.
    """

    power: bool
    setpoint_temperature: Annotated[
        float,
        Field(
            ge=6,
            le=70,
            description="°C. The heat pump takes whole degrees: rounded half up.",
        ),
    ]


def heat_pump_writes(message: HeatPumpSet, slave: int) -> list[RegisterWrite]:
    """The slave's on/off (11) and set point (12), then the global switch (30).

    The bridge applies 11 and 12 when 10 selects the slave; the register map
    only orders 10 after them ("write only after set the 11,12,13 registers").
    The global switch is separate and comes after the batch: the writer stops
    at the first failed write, so a failed batch never leaves the system
    switched.
    """
    setpoint = math.floor(message.setpoint_temperature + 0.5)
    return [
        (REG_DIAG_SPLIT_WRITE_PWR, int(message.power)),
        (REG_DIAG_SPLIT_WRITE_SP_ROOM, to_raw(setpoint, _SETPOINT_FIELD)),
        (REG_DIAG_SPLIT_WRITE_SELECTION, slave),
        (REG_SYSTEM_DISABLE, 0 if message.power else 1),
    ]


def modbus_commands(topics: list[ModbusTopic]) -> list[ModbusCommand[Any]]:
    """Commands for the bridges among ``topics``, on the units they read from."""
    heat_pump = next((t for t in topics if t.topic == HEAT_PUMP_TOPIC), None)
    if heat_pump is None:
        raise ValueError(f"No {HEAT_PUMP_TOPIC} topic to send heat pump commands to")
    return [
        ModbusCommand(
            topic=f"{HEAT_PUMP_TOPIC}/set",
            model=HeatPumpSet,
            unit_id=heat_pump.unit_id,
            to_writes=partial(heat_pump_writes, slave=heat_pump.extra_fields["slave"]),
            description=(
                "Switch the heat pump and set its water temperature; "
                f"{HEAT_PUMP_TOPIC} reads the result back"
            ),
        )
    ]
