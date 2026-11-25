"""MQTT → Modbus: topics whose messages are written to Modbus registers."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from faststream.mqtt import MQTTBroker, QoS
from pydantic import BaseModel

from zero_modbus_bridge.writer import RegisterWrite

logger = logging.getLogger(__name__)


class ModbusCommand[T: BaseModel](BaseModel):
    """One MQTT topic whose messages become Modbus register writes.

    Messages are validated against ``model``; ``to_writes`` turns a valid one
    into the writes, in the order the device needs them.
    """

    model_config = {"arbitrary_types_allowed": True}

    topic: str
    model: type[T]
    unit_id: int = 1
    to_writes: Callable[[T], list[RegisterWrite]]
    description: str | None = None


type CommandWrite = Callable[[ModbusCommand[Any], BaseModel], Awaitable[None]]


def register_commands(
    broker: MQTTBroker, commands: list[ModbusCommand[Any]], write: CommandWrite
) -> None:
    """Subscribe ``broker`` to every command topic, passing valid messages to ``write``.

    A message that fails validation is rejected by FastStream before ``write``
    sees it.
    """
    for command in commands:
        broker.subscriber(
            command.topic,
            qos=QoS.AT_LEAST_ONCE,
            description=command.description or f"Modbus command for {command.topic}",
        )(_handler(command, write))


def _handler(
    command: ModbusCommand[Any], write: CommandWrite
) -> Callable[[BaseModel], Awaitable[None]]:
    async def handle(message: BaseModel) -> None:
        logger.info("Command on %s: %s", command.topic, message.model_dump_json())
        await write(command, message)

    # FastStream validates the payload against the parameter's annotation,
    # which is only known per command.
    handle.__annotations__ = {"message": command.model, "return": None}
    return handle
