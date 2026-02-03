# Adapted from THRS messaging (zero-thrs-control/src/thrs/graphql/messaging.py)

import asyncio
import logging
from typing import Any, Callable, Coroutine

from aiomqtt import Client as MqttClient
from aiomqtt import Message

from loads.registry import MessagingModule, VariableDefinition
from loads.sensors import LoadsModel

from .types import ActualType

logger = logging.getLogger(__name__)


class MessageReceiver[T: LoadsModel]:
    """Receiver for MQTT messages of a specific type and topic."""

    def __init__(self, cls: type[T], topic: str):
        self._cls = cls
        self._last: T | None = None
        self._waiting = False
        self._msgs = asyncio.Queue[T]()
        self._topic = topic

    @property
    def last(self) -> T | None:
        return self._last

    def wait_for(
        self, condition: Callable[[T], bool], timeout: float
    ) -> Coroutine[None, None, T]:
        # Waiting is done a bit awkwardly to ensure self._waiting is True directly after the call
        # Otherwise we might miss message if those arrive right after calling this function
        # and before asyncio ran `self._waiting = True`
        self._waiting = True

        async def _wait():
            async with asyncio.timeout(timeout):
                try:
                    while True:
                        msg = await self._msgs.get()
                        if condition(msg):
                            return msg
                finally:
                    self._waiting = False

        return _wait()

    async def handle(self, msg: T):
        self._last = msg
        if self._waiting:
            await self._msgs.put(msg)

    @property
    def cls(self):
        return self._cls

    @property
    def topic(self):
        return self._topic


class Messaging:
    """Messaging system handling MQTT messages and dispatching them to appropriate receivers."""

    def __init__(
        self,
        mqtt_client: MqttClient,
        modules: list[MessagingModule],
        variable_definitions: dict[str, VariableDefinition],
    ):
        self._mqtt_client = mqtt_client
        self._modules = modules
        self._variable_definitions = variable_definitions
        self._receivers: dict[str, MessageReceiver] = {
            topic: MessageReceiver(cls=model, topic=topic)
            for module in self._modules
            for topic, model in module._mapping.items()
        }

    async def run(self) -> Coroutine[Any, Any, None]:
        for module in self._modules:
            topics = set(module.topics)
            for topic in topics:
                await self._mqtt_client.subscribe(topic, qos=1)

        async def _run(self):
            async for message in self._mqtt_client.messages:
                if message.payload == b"":
                    continue

                if receiver := self._match_receiver(message):
                    await receiver.handle(self._parse_message(message, receiver.cls))

        return _run(self)

    def _match_receiver(self, message: Message) -> MessageReceiver | None:
        return self._receivers.get(message.topic.value, None)

    def _parse_message[T: LoadsModel](self, message: Message, model: type[T]) -> T:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        return model.parse_message_payload(message.payload)

    def get_values_for(self, variable_ids: list[str]) -> list[ActualType]:
        results: list[ActualType] = []
        for variable_id in variable_ids:
            if variable := self._variable_definitions.get(variable_id):
                receiver = self._receivers[variable.topic]

                if receiver.last is None:
                    continue

                results.append(
                    ActualType(
                        id=variable_id,
                        value=variable.get_actual(receiver.last),
                    )
                )
            else:
                raise ValueError(f"{variable_id} is not defined.")

        return results

    def get_variable_definition(self, variable: str) -> VariableDefinition | None:
        return self._variable_definitions.get(variable)
