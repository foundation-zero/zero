from pyModbusTCP.client import ModbusClient

from zero_domestic_control.config import Settings
from zero_domestic_control.mqtt import (
    ControlSend,
)
from .constants import (
    AddressRange,
    ACTUAL_TEMPERATURE_START_ADDRESS,
    TEMPERATURE_SETPOINT_START_ADDRESS,
    ACTUAL_HUMIDITY_START_ADDRESS,
    HUMIDITY_SETPOINT_START_ADDRESS,
    ACTUAL_CO2_START_ADDRESS,
    CO2_SETPOINT_START_ADDRESS,
)


class TermodinamicaAc:
    """Interface to the Termodinamica AC system"""

    def __init__(self, client: ModbusClient):
        self._client = client

    def _read(self, room: str, address_range: AddressRange) -> float:
        address = address_range.address_for_room(room)
        result = self._client.read_holding_registers(address, 1)
        if result is None:
            raise ValueError(f"failed to read {address}")

        return address_range.scale_to_real(result[0])

    def _write(self, room: str, address_range: AddressRange, value: float) -> None:
        address = address_range.address_for_room(room)
        modbus_value = address_range.scale_to_modbus(value)
        result = self._client.write_single_register(address, modbus_value)
        if result is None:
            raise ValueError(f"failed to write {address}")

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

    # CO2
    def read_room_co2(self, room: str) -> float:
        return self._read(room, ACTUAL_CO2_START_ADDRESS)

    def read_room_co2_setpoint(self, room: str) -> float:
        return self._read(room, CO2_SETPOINT_START_ADDRESS)

    def write_room_co2_setpoint(self, room: str, value: float) -> None:
        return self._write(room, CO2_SETPOINT_START_ADDRESS, value)

    @staticmethod
    def init_from_settings(settings: Settings):
        client = ModbusClient(
            host=settings.termodinamica_host, port=settings.termodinamica_port
        )
        return TermodinamicaAc(client)


class Ac:
    """Interface to the AC control"""

    def __init__(self, control: ControlSend):
        self._control = control

    async def write_room_temperature_setpoint(self, room: str, temperature: float):
        await self._control.send_room_temperature_setpoint(room, temperature)

    async def write_room_humidity_setpoint(self, room: str, humidity: float):
        await self._control.send_room_humidity_setpoint(room, humidity)

    async def write_room_co2_setpoint(self, room: str, co2: float):
        await self._control.send_room_co2_setpoint(room, co2)
