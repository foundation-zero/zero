import asyncio
from asyncio import Queue
from typing import Callable, Coroutine

from aiomqtt import Client as MqttClient
from aiomqtt import Message

from loads.sensors import LoadsModel


class MessageReceiver[T: LoadsModel]:
    """Receiver for MQTT messages of a specific type and topic."""

    def __init__(self, cls: type[T], topic: str):
        self._cls = cls
        self._last: T | None = None
        self._waiting = False
        self._msgs = Queue[T]()
        self._topic = topic

    @property
    def last(self) -> T | None:
        return self._last

    def wait_for(self, condition: Callable[[T], bool], timeout: float) -> Coroutine[None, None, T]:
        # Waiting is done a bit awkward to ensure self._waiting is True directly after the call
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


class MessagingModule:
    """Module handling multiple validators for different topics."""

    def __init__(self, validators: list[type[LoadsModel]]) -> None:
        self._validators = validators
        self._mapping = {validator.TOPIC: validator for validator in validators}

    @property
    def topics(self) -> list[str]:
        return list(self._mapping.keys())

    def model_validate_json(self, data: str | bytes, topic: str):
        component = self._mapping[topic]
        return component.model_validate_json(data)

    def gen_config(self):
        return [item for validator in self._validators for item in validator.gen_config()]


class Messaging:
    """Messaging system handling MQTT messages and dispatching them to appropriate receivers."""

    def __init__(
        self,
        mqtt_client: MqttClient,
        modules: list[MessagingModule],
    ):
        self._mqtt_client: MqttClient = mqtt_client
        self._modules: list[MessagingModule] = modules
        self._receivers: dict[str, MessageReceiver] = {
            topic: MessageReceiver(cls=receiver, topic=topic)
            for module in self._modules
            for topic, receiver in module._mapping.items()
        }

    async def run(self) -> Coroutine[None, None, None]:
        for module in self._modules:
            topics = set(module.topics)
            for topic in topics:
                await self._mqtt_client.subscribe(topic, qos=1)

        async def _run(self):
            async for message in self._mqtt_client.messages:
                if message.payload == b"":
                    continue

                if receiver := self.match_receiver(message):
                    await receiver.handle(self._parse_message(message, receiver.cls))

        return _run(self)

    def match_receiver(self, message: Message) -> MessageReceiver | None:
        return self._receivers.get(str(message.topic), None)

    def _parse_message[T: LoadsModel](self, message: Message, model: type[T]) -> T:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        return model.model_validate_json(message.payload)
