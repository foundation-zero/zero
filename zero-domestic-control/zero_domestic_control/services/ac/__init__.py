from abc import ABC, abstractmethod
from asyncio import TaskGroup, sleep
import asyncio
from dataclasses import dataclass
from functools import partial
from typing import Callable, Generator, assert_never
from pyModbusTCP.client import ModbusClient

from zero_domestic_control.config import Settings
from zero_domestic_control.messages import (
    Room,
    RoomTemperatureSetpoint,
)
from zero_domestic_control.mqtt import (
    ControlMessages,
    ControlReceive,
    ControlSend,
    DataCollection,
)
from zero_domestic_control.services.ac.thrs import Thrs

ROOM_INDICES = {
    "owners-cabin": 0,
    "dutch-cabin": 1,
    "french-cabin": 2,
    "italian-cabin": 3,
    "californian-lounge": 4,
    "polynesian-cabin": 5,
    "galley": 6,
    "crew-mess": 7,
    "mission-room": 8,
    "laundry": 9,
    "engineers-office": 10,
    "captains-cabin": 11,
    "crew-sb-aft-cabin": 12,
    "crew-sb-mid-cabin": 13,
    "crew-sb-fwd-cabin": 14,
    "crew-ps-mid-cabin": 15,
    "crew-ps-fwd-cabin": 16,
    "owners-deckhouse": 17,
    "owners-cockpit": 18,
    "main-deckhouse": 19,
    "main-cockpit": 20,
    "owners-stairway": 21,
    "guest-corridor": 22,
    "polynesian-corridor": 23,
}


@dataclass
class AddressRange:
    """Denotes a modbus address range for a specific property with entries for each room"""

    start: int
    """scaling factor from modbus to real (so if modbus temperature is 200, then scale would be 0.1)"""
    scale: float

    def scale_to_real(self, modbus_value: float) -> float:
        return self.scale * modbus_value

    def scale_to_modbus(self, real_value: float) -> float:
        return int(real_value / self.scale)

    def address_for_room(self, room: str) -> int:
        return self.start + ROOM_INDICES[room]


# TODO: correct these to the actual addresses when we receive those
ACTUAL_TEMPERATURE_START_ADDRESS = AddressRange(100, 0.1)
TEMPERATURE_SETPOINT_START_ADDRESS = AddressRange(200, 0.1)
ACTUAL_HUMIDITY_START_ADDRESS = AddressRange(300, 1)
HUMIDITY_SETPOINT_START_ADDRESS = AddressRange(400, 1)


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

    def read_room_temperature(self, room: str) -> float:
        return self._read(room, ACTUAL_TEMPERATURE_START_ADDRESS)

    def read_room_temperature_setpoint(self, room: str) -> float:
        return self._read(room, TEMPERATURE_SETPOINT_START_ADDRESS)

    def write_room_temperature_setpoint(self, room: str, value: float) -> None:
        return self._write(room, TEMPERATURE_SETPOINT_START_ADDRESS, value)

    def read_room_humidity(self, room: str) -> float:
        return self._read(room, ACTUAL_HUMIDITY_START_ADDRESS)

    def read_room_humidity_setpoint(self, room: str) -> float:
        return self._read(room, HUMIDITY_SETPOINT_START_ADDRESS)

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
        await self._control.send_room_setpoint(room, temperature)


@dataclass
class AcTempChange:
    room: str
    temperature: float


type CommOp = Callable[[], None]


@dataclass
class TermodinamicaUpdate:
    room: str
    value: "AcProperty"


class AcProperty(ABC):
    value: float

    @staticmethod
    @abstractmethod
    def get(room: Room) -> float | None: ...

    @abstractmethod
    def set(self, room: Room): ...


@dataclass
class ActualTemperature(AcProperty):
    value: float

    @staticmethod
    def get(room: Room) -> float | None:
        return room.actual_temperature

    def set(self, room: Room):
        room.actual_temperature = self.value


@dataclass
class TemperatureSetpoint(AcProperty):
    value: float

    @staticmethod
    def get(room: Room) -> float | None:
        return room.temperature_setpoint

    def set(self, room: Room):
        room.temperature_setpoint = self.value


@dataclass
class ActualHumidity(AcProperty):
    value: float

    @staticmethod
    def get(room: Room) -> float | None:
        return room.actual_humidity

    def set(self, room: Room):
        room.actual_humidity = self.value


@dataclass
class HumiditySetpoint(AcProperty):
    value: float

    @staticmethod
    def get(room: Room) -> float | None:
        return room.humidity_setpoint

    def set(self, room: Room):
        room.humidity_setpoint = self.value


AC_CONTROL_BUS_INTERVAL = 0.1  # 100 ms


class AcControl:
    """This class is responsible for balancing the control messages between the control system and the termodinamica system

    Managing Termodinamica comms means looping through the rooms and their properties and checking if the values have changed.
    This is done in a single process to prevent overloading the system with too many requests.
    Queues are used to communicate between the different parts of the system.
    _write_ops contains the write requests to the Termonidamica bus
    _control_messages is used to signal a change to the control process
    """

    def __init__(
        self,
        receiver: ControlReceive,
        termodinamica: TermodinamicaAc,
        thrs: Thrs,
        data_collection: DataCollection,
    ):
        self._receiver = receiver
        self._control_messages: asyncio.Queue[ControlMessages | TermodinamicaUpdate] = (
            asyncio.Queue()
        )
        self._rooms = {
            id: Room(
                id=id,
                actual_temperature=None,
                temperature_setpoint=None,
                actual_humidity=None,
                humidity_setpoint=None,
                amplifier_on=None,
            )
            for id in ROOM_INDICES.keys()
        }
        self._data_collection = data_collection
        self._termodinamica = termodinamica
        self._thrs = thrs
        self._write_ops: asyncio.Queue[CommOp] = asyncio.Queue()

    def read_ops(self) -> Generator[Callable[[], tuple[str, AcProperty]]]:
        def _read_data(op, id, prop):
            result = op(id)
            return id, prop(result)

        while True:
            for op, property in [
                (
                    self._termodinamica.read_room_temperature_setpoint,
                    TemperatureSetpoint,
                ),
                (self._termodinamica.read_room_temperature, ActualTemperature),
                (self._termodinamica.read_room_humidity, ActualHumidity),
                (
                    self._termodinamica.read_room_humidity_setpoint,
                    HumiditySetpoint,
                ),
            ]:
                for room_id in ROOM_INDICES.keys():
                    yield partial(_read_data, op, room_id, property)

    async def _receive_control_messages(self):
        await self._receiver.listen()
        async for message in self._receiver.messages:
            await self._control_messages.put(message)

    async def _termodinamica_comms(self):
        reads = self.read_ops()

        async def _step():
            if not self._write_ops.empty():
                write = await self._write_ops.get()
                write()
            else:
                read = next(reads)
                room_id, property = read()
                old_value = property.get(self._rooms[room_id])
                if old_value != property.value:
                    await self._control_messages.put(
                        TermodinamicaUpdate(room=room_id, value=property)
                    )
                property.set(self._rooms[room_id])

        while True:
            async with TaskGroup() as tg:
                tg.create_task(_step())
                tg.create_task(sleep(AC_CONTROL_BUS_INTERVAL))

    async def _control_systems(self):
        while True:
            message = await self._control_messages.get()
            if isinstance(message, RoomTemperatureSetpoint):
                self._rooms[message.id].temperature_setpoint = message.temperature
                msg: RoomTemperatureSetpoint = (
                    message  # storing message to ensure type in lambda
                )
                await self._write_ops.put(
                    lambda: self._termodinamica.write_room_temperature_setpoint(
                        msg.id, msg.temperature
                    )
                )
                await self._thrs.set_room_temperature_setpoint(msg.id, msg.temperature)
                await self._data_collection.send_room(self._rooms[msg.id])
            elif isinstance(message, TermodinamicaUpdate):
                if isinstance(message.value, TemperatureSetpoint):
                    await self._thrs.set_room_temperature_setpoint(
                        message.room, message.value.value
                    )
                await self._data_collection.send_room(self._rooms[message.room])
            else:
                assert_never(message)

    async def run(self):
        async with TaskGroup() as tg:
            tg.create_task(self._receive_control_messages())
            tg.create_task(self._termodinamica_comms())
            tg.create_task(self._control_systems())
