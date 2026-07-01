from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Awaitable, Callable, Literal, cast

from aiomqtt import Client as MqttClient
from pydantic import Field, ValidationInfo, model_validator

from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues


@dataclass
class MqttContext:
    topic: str

    @property
    def module(self) -> str:
        return self.topic.split("/")[0]


class Messaging:
    def __init__(self, client: MqttClient):
        self._client = client
        self._handlers: list[
            tuple[
                type[IncomingMessage],
                Callable[[IncomingMessage], Awaitable[None]],
            ]
        ] = []

    async def send(self, topic_prefix: str, message: "OutgoingMessage"):
        await self._client.publish(
            f"{topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
            retain=message.retained(),
        )

    async def register[T: "IncomingMessage"](
        self,
        topic_prefix: str,
        message: type[T],
        handler: Callable[[T], Awaitable[None]],
    ):
        await self._client.subscribe(
            f"{topic_prefix}/{message.subscribe_topic()}", qos=1
        )

        async def _wrapped(msg: IncomingMessage) -> None:
            await handler(cast(T, msg))

        self._handlers.append((type(message), _wrapped))

    async def run(self):
        async for msg in self._client.messages:
            for message_type, handler in self._handlers:
                if msg.topic.matches(f"{message_type.subscribe_topic()}"):
                    if not isinstance(msg.payload, str | bytes):
                        raise ValueError("Message payload is not bytes")
                    payload = message_type.model_validate_json(msg.payload)
                    await handler(payload)

    async def clear(self, topic_prefix: str, messages: "list[type[OutgoingMessage]]"):
        for message in messages:
            await self._client.publish(
                f"{topic_prefix}/{message.subscribe_topic()}",
                b"",
                qos=1,
                retain=True,
            )


class IncomingMessage(ThrsValues):
    @staticmethod
    @abstractmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]": ...

    @staticmethod
    @abstractmethod
    def subscribe_topic() -> str: ...

    def topic(self) -> str:
        return self.subscribe_topic()


class IncomingModuleMessage(IncomingMessage):
    module: Annotated[str, Field(exclude=True, default=None)]

    @model_validator(mode="before")
    @classmethod
    def module_from_topic(cls, data: Any, info: ValidationInfo[MqttContext]) -> Any:
        if "module" not in data and info.context:
            data["module"] = info.context.module
        return data


class OutgoingMessage(ThrsValues):
    @staticmethod
    @abstractmethod
    def subscribe_topic() -> str: ...

    @staticmethod
    @abstractmethod
    def retained() -> bool: ...

    def topic(self) -> str:
        return self.subscribe_topic()

    @classmethod
    def clear_topics(cls, control_modules: list[str]) -> list[str]:
        return [cls.subscribe_topic()]


type SimulationStatus = Literal["available", "running", "stepping"]


class SimulationStatusMessage(OutgoingMessage):
    mode: str
    status: SimulationStatus
    control_modules: list[str]
    simulation_time: datetime

    @staticmethod
    def subscribe_topic() -> str:
        return "status"

    @staticmethod
    def retained() -> bool:
        return True


class SimulationInputMessage[Inputs: ThrsValues](OutgoingMessage):
    inputs: Inputs

    @staticmethod
    def subscribe_topic() -> str:
        return "inputs"

    @staticmethod
    def retained() -> bool:
        return True


class PlayMessage(IncomingMessage):
    playback_rate: Annotated[float, Field(ge=0.25, le=10)] = 1.0

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return PlayMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "play"


class StepMessage(IncomingMessage):
    seconds: Annotated[float, Field(ge=0)]

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return StepMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "step"


class PauseMessage(IncomingMessage):
    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return PauseMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "pause"
