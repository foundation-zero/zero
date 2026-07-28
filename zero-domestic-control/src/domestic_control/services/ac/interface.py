from pyModbusTCP.client import ModbusClient

from domestic_control.config import Settings
from domestic_control.mqtt import (
    ControlSend,
)
from domestic_control.services.modbus import ModbusRoomInterface

from .constants import (
    ACTUAL_HUMIDITY_START_ADDRESS,
    ACTUAL_TEMPERATURE_START_ADDRESS,
    HUMIDITY_SETPOINT_START_ADDRESS,
    ROOM_INDICES,
    TEMPERATURE_SETPOINT_START_ADDRESS,
)


class AcInterface(ModbusRoomInterface):
    """Interface to the Termodinamica AC system"""

    def __init__(self, client: ModbusClient):
        super().__init__(client, ROOM_INDICES)

    # Temperature
    def read_room_temperature(self, room: str) -> float:
        return self._read(room, ACTUAL_TEMPERATURE_START_ADDRESS)

    def read_room_temperature_setpoint(self, room: str) -> float:
        return self._read(room, TEMPERATURE_SETPOINT_START_ADDRESS)

    def write_room_temperature_setpoint(self, room: str, value: float) -> None:
        return self._write(room, TEMPERATURE_SETPOINT_START_ADDRESS, value)

    # Humidity
    def read_room_humidity(self, room: str) -> float:
        return self._read(room, ACTUAL_HUMIDITY_START_ADDRESS)

    def read_room_humidity_setpoint(self, room: str) -> float:
        return self._read(room, HUMIDITY_SETPOINT_START_ADDRESS)

    def write_room_humidity_setpoint(self, room: str, value: float) -> None:
        return self._write(room, HUMIDITY_SETPOINT_START_ADDRESS, value)

    @staticmethod
    def init_from_settings(settings: Settings):
        client = ModbusClient(
            host=settings.air_conditioning_host, port=settings.air_conditioning_port
        )
        return AcInterface(client)


class Ac:
    """Interface to the AC control"""

    def __init__(self, control: ControlSend):
        self._control = control
        self._rooms = ROOM_INDICES.keys()

    async def write_room_temperature_setpoint(self, room: str, temperature: float):
        self.validate_room_id(room)
        await self._control.send_room_temperature_setpoint(room, temperature)

    async def write_room_humidity_setpoint(self, room: str, humidity: float):
        self.validate_room_id(room)
        await self._control.send_room_humidity_setpoint(room, humidity)

    def validate_room_id(self, id: str):
        if id not in self._rooms:
            raise ValueError(f"Invalid room ID {id}")

    def validate_room_ids(self, ids: list[str]):
        if invalid := set(ids) - set(self._rooms):
            raise ValueError(f"Invalid room IDs {invalid}")
