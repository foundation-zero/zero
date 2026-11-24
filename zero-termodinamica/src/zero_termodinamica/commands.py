"""Commands that MQTT clients (such as thrs) send to the Termodinamica bridges."""

from typing import Annotated, Any

from pydantic import BaseModel, Field
from zero_modbus_bridge.commands import ModbusCommand
from zero_modbus_bridge.io import ModbusTopic
from zero_modbus_bridge.writer import RegisterWrite

HEAT_PUMP_TOPIC = "termodinamica/heat-pump"

# Base register map (docs/BridgeExchangeDataAddressMap_Rev Fw 8.14.17).
REG_DIAG_SPLIT_WRITE_SELECTION = 10
REG_DIAG_SPLIT_WRITE_PWR = 11
REG_DIAG_SPLIT_WRITE_SP_ROOM = 12
REG_SYSTEM_DISABLE = 30

# The heat pump is slave unit 2 on its bridge; slot 1 only holds placeholders.
HEAT_PUMP_SLAVE = 2


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
            description="°C. The heat pump takes whole degrees, so it is rounded.",
        ),
    ]


def heat_pump_writes(message: HeatPumpSet) -> list[RegisterWrite]:
    """The global switch (30) plus the slave's on/off (11) and set point (12).

    The bridge applies 11 and 12 when 10 selects the slave, so 10 goes last.
    Switching on enables the system before the unit, switching off the reverse.
    """
    unit = [
        (REG_DIAG_SPLIT_WRITE_PWR, int(message.power)),
        (REG_DIAG_SPLIT_WRITE_SP_ROOM, round(message.setpoint_temperature) * 100),
        (REG_DIAG_SPLIT_WRITE_SELECTION, HEAT_PUMP_SLAVE),
    ]
    system = [(REG_SYSTEM_DISABLE, 0 if message.power else 1)]
    return system + unit if message.power else unit + system


def modbus_commands(topics: list[ModbusTopic]) -> list[ModbusCommand[Any]]:
    """Commands for the bridges among ``topics``, on the units they read from."""
    heat_pump = next(t for t in topics if t.topic == HEAT_PUMP_TOPIC)
    return [
        ModbusCommand(
            topic=f"{HEAT_PUMP_TOPIC}/set",
            model=HeatPumpSet,
            unit_id=heat_pump.unit_id,
            to_writes=heat_pump_writes,
            description=(
                "Switch the heat pump and set its water temperature; "
                f"{HEAT_PUMP_TOPIC} reads the result back"
            ),
        )
    ]
