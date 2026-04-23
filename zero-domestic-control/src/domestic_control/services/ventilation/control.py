from asyncio import TaskGroup, sleep
import asyncio
from functools import partial
from typing import Callable, Coroutine, Generator, assert_never

from domestic_control.messages import (
    Ventilation,
    RoomCo2Setpoint,
)
from domestic_control.mqtt import (
    ControlReceive,
)
from domestic_control.sink import Sink
from .interface import VentilationInterface
from .properties import (
    VentilationUpdate,
    VentilationProperty,
    ActualCo2,
    Co2Setpoint,
)
from .constants import ROOM_INDICES
import logging

VENTILATION_CONTROL_BUS_INTERVAL_SEC = 0.1  # 100 ms

type CommOp = Callable[[], None]

logger = logging.getLogger(__name__)


class VentilationControl:
    """This class is responsible for balancing the control messages between the control system and the ventilation system

    Managing ventilation comms means looping through the rooms and their properties and checking if the values have changed.
    This is done in a single process to prevent overloading the system with too many requests.
    Queues are used to communicate between the different parts of the system.
    _write_ops contains the write requests to the ventilation bus
    _control_messages is used to signal a change to the control process
    """

    def __init__(
        self,
        receiver: ControlReceive,
        ventilation: VentilationInterface,
        data_collection: Sink,
    ):
        self._receiver = receiver
        self._control_messages: asyncio.Queue[RoomCo2Setpoint | VentilationUpdate] = (
            asyncio.Queue()
        )
        self._rooms = {
            id: Ventilation(
                id=id,
                actual_co2=None,
                co2_setpoint=None,
            )
            for id in ROOM_INDICES.keys()
        }
        self._data_collection = data_collection
        self._ventilation = ventilation
        self._write_ops: asyncio.Queue[CommOp] = asyncio.Queue()

    def read_ops(self) -> Generator[Callable[[], tuple[str, VentilationProperty]]]:
        def _read_data(op, id, prop):
            result = op(id)
            return id, prop(result)

        while True:
            for op, property in [
                (
                    self._ventilation.read_room_co2_setpoint,
                    Co2Setpoint,
                ),
                (self._ventilation.read_room_co2, ActualCo2),
            ]:
                for room_id in ROOM_INDICES.keys():
                    yield partial(_read_data, op, room_id, property)

    async def _receive_control_messages(self):
        async for message in self._receiver.messages:
            if isinstance(message, RoomCo2Setpoint):
                await self._control_messages.put(message)

    async def _ventilation_comms(self):
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
                    logging.debug(
                        f"Update for {room_id} {property}. Old value: {old_value}"
                    )
                    await self._control_messages.put(
                        VentilationUpdate(room=room_id, value=property)
                    )
                    property.set(self._rooms[room_id])

        while True:
            async with TaskGroup() as tg:
                tg.create_task(_step())
                tg.create_task(sleep(VENTILATION_CONTROL_BUS_INTERVAL_SEC))

    async def _control_systems(self):
        while True:
            message = await self._control_messages.get()
            if isinstance(message, RoomCo2Setpoint):
                self._rooms[message.id].co2_setpoint = message.co2
                msg_co2: RoomCo2Setpoint = message
                logging.info(f"CO2 setpoint changed: {message.id}: {message.co2}")
                await self._write_ops.put(
                    partial(
                        self._ventilation.write_room_co2_setpoint,
                        msg_co2.id,
                        msg_co2.co2,
                    )
                )
                await self._data_collection.send(self._rooms[message.id])
            elif isinstance(message, VentilationUpdate):
                logging.info(
                    f"Ventilation update received: {message.room}: {message.value}"
                )
                await self._data_collection.send(self._rooms[message.room])
            else:
                assert_never(message)  # type: ignore

    async def run(self) -> Coroutine[None, None, None]:
        """Run the VentilationControl service.

        The returned awaitable finishes when the control is actually running.
        Then the coroutine contained within can be run in an event loop.
        """
        await self._receiver.listen()

        async def _run():
            async with TaskGroup() as tg:
                tg.create_task(self._receive_control_messages())
                tg.create_task(self._ventilation_comms())
                tg.create_task(self._control_systems())

        return _run()
