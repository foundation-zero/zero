from __future__ import annotations

from abc import abstractmethod
from asyncio import Queue
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
)

from aiomqtt import Client as MqttClient
from pydantic import (
    Field,
    ValidationInfo,
    model_validator,
)

from src.thrs.orchestration.module import CombinedControl
from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)

if TYPE_CHECKING:
    from src.thrs.cli.runner.messaging import SimulationCtrlMessage

@dataclass
class MqttContext:
    topic: str

    @property
    def module(self) -> str:
        return self.topic.split("/")[0]


@dataclass
class MessageContext[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    Parameters: ThrsValues,
    Inputs: SimulationInputs,
    Outputs: SimulationValues,
]:
    cmds: Queue["SimulationCtrlMessage"]
    control: CombinedControl
    client: MqttClient
    # executor: SimulationExecutor[
    #     SensorValues,
    #     ControlValues,
    #     Inputs,
    #     Outputs,
    # ]
    topic_prefix: str

    async def send(self, message: "OutgoingMessage"):
        await self.client.publish(
            f"{self.topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
            retain=message.retained(),
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

    @abstractmethod
    async def handle(self, context: MessageContext): ...


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
