# Adapted from THRS messaging (zero-thrs-control/src/thrs/graphql/messaging.py)

import asyncio
import logging
from typing import Any, Callable, Coroutine

from aiomqtt import Client as MqttClient
from aiomqtt import Message
from pydantic import ValidationError

from loads.registry import AlarmDefinition, MessagingModule, VariableDefinition
from loads.sensors import LoadsModel

logger = logging.getLogger(__name__)


class MessageReceiver[T: LoadsModel]:
    """Receiver for MQTT messages of a specific type and topic."""

    def __init__(self, cls: type[T], topic: str):
        self._cls = cls
        self._last: T | None = None
        self._msgs = asyncio.Queue[T]()
        self._topic = topic

    @property
    def last(self) -> T | None:
        return self._last

    async def handle(self, msg: T):
        self._last = msg

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
        alarm_definitions: dict[str, AlarmDefinition],
    ):
        self._mqtt_client = mqtt_client
        self._modules = modules
        self._variable_definitions = variable_definitions
        self._alarm_definitions = alarm_definitions
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
                    if parsed := self._parse_message(message, receiver.cls):
                        await receiver.handle(parsed)

        return _run(self)

    def _match_receiver(self, message: Message) -> MessageReceiver | None:
        return self._receivers.get(message.topic.value, None)

    def _parse_message[T: LoadsModel](
        self, message: Message, model: type[T]
    ) -> T | None:
        if not isinstance(message.payload, str | bytes):
            raise ValueError(f"Expected string or bytes, got {type(message.payload)}")
        try:
            return model.parse_message_payload(message.payload)
        except ValidationError as e:
            logger.error(
                f"Failed to parse message payload for topic {message.topic.value}: {e}"
            )
            return None

    def get_variable_value(self, variable_id: str) -> float | None:
        if variable := self._variable_definitions.get(variable_id):
            receiver = self._receivers[variable.topic]

            if receiver.last is None:
                return None

            return variable.get_actual(receiver.last)
        else:
            raise ValueError(f"Variable {variable_id} is not defined.")

    def _get_alarm_value[T](
        self,
        alarm_id: str,
        value: Callable[[AlarmDefinition], Callable[[LoadsModel], T]],
    ) -> T | None:
        if alarm := self._alarm_definitions.get(alarm_id):
            receiver = self._receivers[alarm.topic]

            if receiver.last is None:
                return None

            return value(alarm)(receiver.last)
        else:
            raise ValueError(f"Alarm {alarm_id} is not defined.")

    def get_alarm_active_for(self, alarm_id: str) -> bool | None:
        return self._get_alarm_value(alarm_id, lambda alarm: alarm.get_active)

    def get_alarm_actual_for(self, alarm_id: str) -> float | None:
        return self._get_alarm_value(alarm_id, lambda alarm: alarm.get_actual)

    def get_alarm_threshold_for(self, alarm_id: str) -> float | None:
        return self._get_alarm_value(alarm_id, lambda alarm: alarm.get_threshold)

    def get_variable_definition(self, variable: str) -> VariableDefinition | None:
        return self._variable_definitions.get(variable)
