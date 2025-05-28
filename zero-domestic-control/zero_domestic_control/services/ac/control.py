from asyncio import TaskGroup, sleep
import asyncio
from functools import partial
from typing import Callable, Generator, assert_never

from zero_domestic_control.messages import (
    Room,
    RoomTemperatureSetpoint,
    RoomHumiditySetpoint,
    RoomCo2Setpoint,
)
from zero_domestic_control.mqtt import (
    ControlMessages,
    ControlReceive,
    DataCollection,
)
from zero_domestic_control.services.ac.thrs import Thrs
from .interface import TermodinamicaAc
from .properties import (
    TermodinamicaUpdate,
    AcProperty,
    TemperatureSetpoint,
    ActualTemperature,
    ActualHumidity,
    HumiditySetpoint,
    ActualCo2,
    Co2Setpoint,
)
from .constants import ROOM_INDICES

AC_CONTROL_BUS_INTERVAL = 0.1  # 100 ms

type CommOp = Callable[[], None]


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
                actual_co2=None,
                co2_setpoint=None,
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
                (
                    self._termodinamica.read_room_humidity_setpoint,
                    HumiditySetpoint,
                ),
                (self._termodinamica.read_room_humidity, ActualHumidity),
                (
                    self._termodinamica.read_room_co2_setpoint,
                    Co2Setpoint,
                ),
                (self._termodinamica.read_room_co2, ActualCo2),
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
                # storing message to ensure type in lambda
                msg_temp: RoomTemperatureSetpoint = message
                await self._write_ops.put(
                    lambda: self._termodinamica.write_room_temperature_setpoint(
                        msg_temp.id, msg_temp.temperature
                    )
                )
                await self._thrs.set_room_temperature_setpoint(
                    msg_temp.id, msg_temp.temperature
                )
                await self._data_collection.send_room(self._rooms[message.id])
            elif isinstance(message, RoomHumiditySetpoint):
                self._rooms[message.id].humidity_setpoint = message.humidity
                msg_hum: RoomHumiditySetpoint = message
                await self._write_ops.put(
                    lambda: self._termodinamica.write_room_humidity_setpoint(
                        msg_hum.id, msg_hum.humidity
                    )
                )
                await self._thrs.set_room_humidity_setpoint(
                    msg_hum.id, msg_hum.humidity
                )
                await self._data_collection.send_room(self._rooms[message.id])
            elif isinstance(message, RoomCo2Setpoint):
                self._rooms[message.id].co2_setpoint = message.co2
                msg_co2: RoomCo2Setpoint = message
                await self._write_ops.put(
                    lambda: self._termodinamica.write_room_co2_setpoint(
                        msg_co2.id, msg_co2.co2
                    )
                )
                await self._thrs.set_room_co2_setpoint(msg_co2.id, msg_co2.co2)
                await self._data_collection.send_room(self._rooms[message.id])
            elif isinstance(message, TermodinamicaUpdate):
                if isinstance(message.value, TemperatureSetpoint):
                    await self._thrs.set_room_temperature_setpoint(
                        message.room, message.value.value
                    )
                elif isinstance(message.value, HumiditySetpoint):
                    await self._thrs.set_room_humidity_setpoint(
                        message.room, message.value.value
                    )
                elif isinstance(message.value, Co2Setpoint):
                    await self._thrs.set_room_co2_setpoint(
                        message.room, message.value.value
                    )
                await self._data_collection.send_room(self._rooms[message.room])
            else:
                assert_never(message)  # type: ignore

    async def run(self):
        async with TaskGroup() as tg:
            tg.create_task(self._receive_control_messages())
            tg.create_task(self._termodinamica_comms())
            tg.create_task(self._control_systems())
