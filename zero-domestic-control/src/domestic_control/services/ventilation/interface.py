from pyModbusTCP.client import ModbusClient

from domestic_control.config import Settings
from domestic_control.mqtt import ControlSend
from domestic_control.services.modbus import ModbusRoomInterface
from .constants import (
    ACTUAL_CO2_START_ADDRESS,
    CO2_SETPOINT_START_ADDRESS,
    ROOM_INDICES,
)


class VentilationInterface(ModbusRoomInterface):
    """Interface to the ventilation system via Modbus"""

    def __init__(self, client: ModbusClient):
        super().__init__(client, ROOM_INDICES)

    def read_room_co2(self, room: str) -> float:
        return self._read(room, ACTUAL_CO2_START_ADDRESS)

    def read_room_co2_setpoint(self, room: str) -> float:
        return self._read(room, CO2_SETPOINT_START_ADDRESS)

    def write_room_co2_setpoint(self, room: str, value: float) -> None:
        return self._write(room, CO2_SETPOINT_START_ADDRESS, value)

    @staticmethod
    def init_from_settings(settings: Settings):
        client = ModbusClient(
            host=settings.ventilation_host, port=settings.ventilation_port
        )
        return VentilationInterface(client)


class Ventilation:
    """Interface to the ventilation control"""

    def __init__(self, control: ControlSend):
        self._control = control
        self._rooms = ROOM_INDICES.keys()

    async def write_room_co2_setpoint(self, room: str, co2: float):
        self.validate_room_id(room)
        await self._control.send_room_co2_setpoint(room, co2)

    def validate_room_id(self, id: str):
        if id not in self._rooms:
            raise ValueError(f"Invalid room ID {id}")

    def validate_room_ids(self, ids: list[str]):
        if invalid := set(ids) - set(self._rooms):
            raise ValueError(f"Invalid room IDs {invalid}")
