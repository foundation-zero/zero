from dataclasses import dataclass
from collections.abc import Mapping

from pyModbusTCP.client import ModbusClient
import logging


@dataclass
class AddressRange:
    """Modbus base address and value scaling for a room property."""

    start: int
    scale: float

    def scale_to_real(self, modbus_value: float) -> float:
        return self.scale * modbus_value

    def scale_to_modbus(self, real_value: float) -> float:
        return int(real_value / self.scale)

    def address_for_room(self, room: str, room_indices: Mapping[str, int]) -> int:
        return self.start + room_indices[room]


class ModbusRoomInterface:
    """Shared Modbus read/write helpers for room-based services."""

    def __init__(self, client: ModbusClient, room_indices: Mapping[str, int]):
        self._client = client
        self._room_indices = room_indices

    def _read(self, room: str, address_range: AddressRange) -> float:
        logging.debug(f"Reading {address_range} for room {room}")
        address = address_range.address_for_room(room, self._room_indices)
        result = self._client.read_holding_registers(address, 1)
        if result is None:
            raise ValueError(f"failed to read {address}")

        return address_range.scale_to_real(result[0])

    def _write(self, room: str, address_range: AddressRange, value: float) -> None:
        logging.debug(f"Writing {value} to {address_range} for room {room}")
        address = address_range.address_for_room(room, self._room_indices)
        modbus_value = address_range.scale_to_modbus(value)
        result = self._client.write_single_register(address, modbus_value)
        if result is None:
            raise ValueError(f"failed to write {address}")
