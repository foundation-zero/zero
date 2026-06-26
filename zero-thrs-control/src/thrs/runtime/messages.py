from abc import abstractmethod
from asyncio import Queue
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Literal

from aiomqtt import Client as MqttClient
from pydantic import Field, ValidationInfo, model_validator

from thrs.control.switching import SwitchingControlMode
from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.orchestration.module import CombinedControl
from thrs.orchestration.simulation import Simulation


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
    Inputs: SimulationInputs,
    Outputs: SimulationValues,
]:
    cmds: "Queue[SimulationCtrlMessage]"
    control: CombinedControl
    client: MqttClient
    simulation: Simulation[
        SensorValues,
        ControlValues,
        Inputs,
        Outputs,
    ]

    async def send(self, topic_prefix: str, message: "OutgoingMessage"):
        await self.client.publish(
            f"{topic_prefix}/{message.topic()}",
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
    async def handle(self, topic_prefix: str, context: MessageContext): ...


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


class SimulationStatusMessage(OutgoingMessage):
    mode: str
    status: Literal["available", "running", "stepping"]
    control_modules: list[str]
    simulation_time: datetime

    @staticmethod
    def subscribe_topic() -> str:
        return "status"

    @staticmethod
    def retained() -> bool:
        return True


class ControlModeMessage[ControlMode](OutgoingMessage):
    module: str
    mode: SwitchingControlMode[ControlMode]

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/status"

    def topic(self) -> str:
        return f"{self.module}/controls/status"

    @classmethod
    def clear_topics(cls, control_modules: list[str]) -> list[str]:
        return [f"{module}/controls/status" for module in control_modules]

    @staticmethod
    def retained() -> bool:
        return True


class ParametersMessage[Parameters: ThrsValues](OutgoingMessage):
    parameters: Parameters
    module: str

    @staticmethod
    def subscribe_topic() -> str:
        return "+/config/parameters"

    def topic(self) -> str:
        return f"{self.module}/config/parameters"

    @classmethod
    def clear_topics(cls, control_modules: list[str]) -> list[str]:
        return [f"{module}/config/parameters" for module in control_modules]

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


SIMULATION_OUTGOING_MESSAGES = [
    SimulationStatusMessage,
    SimulationInputMessage,
]

CONTROLLER_OUTGOING_MESSAGES = [
    ControlModeMessage,
    ParametersMessage,
]


class SimulationCtrlMessage(IncomingMessage):
    async def handle(self, topic_prefix: str, context: MessageContext):
        await context.cmds.put(self)


class SimulationPlayMessage(SimulationCtrlMessage):
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
        return SimulationPlayMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "play"


class SimulationStepMessage(SimulationCtrlMessage):
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
        return SimulationStepMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "step"


class SimulationPauseMessage(SimulationCtrlMessage):
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
        return SimulationPauseMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "pause"


class ManualControlMessage[ControlValues: ThrsValues](IncomingModuleMessage):
    control_values: ControlValues

    @staticmethod
    def resolve[
        LControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[LControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return ManualControlMessage[control_values]

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/manual"

    def topic(self):
        return f"{self.module}/controls/manual"

    async def handle(
        self,
        topic_prefix: str,
        context: MessageContext[
            ThrsValues, ControlValues, SimulationInputs, SimulationValues
        ],
    ):
        context.control.manual_controls(self.module, self.control_values)


class SetAutomationMessage(IncomingModuleMessage):
    enabled: bool

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
        return SetAutomationMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/set_automation"

    def topic(self):
        return f"{self.module}/controls/set_automation"

    async def handle(self, topic_prefix: str, context: MessageContext):
        context.control.set_automation_mode(self.module, self.enabled)
        await context.send(
            topic_prefix,
            ControlModeMessage(
                module=self.module,
                mode=context.control.mode_for(self.module),
            ),
        )


class SetParametersMessage[Parameters: ThrsValues](IncomingModuleMessage):
    parameters: Parameters

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        LParameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[LParameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return SetParametersMessage[parameters]

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/set_parameters"

    def topic(self):
        return f"{self.module}/controls/set_parameters"

    async def handle(
        self, topic_prefix: str, context: MessageContext[Any, Any, Any, Any]
    ):
        context.control.update_parameters_for(self.module, self.parameters)
        await context.send(
            topic_prefix,
            ParametersMessage(
                parameters=context.control.parameters.values[self.module],
                module=self.module,
            ),
        )


class SetSimulationInputsMessage[Inputs: SimulationInputs](IncomingMessage):
    inputs: Inputs

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        LInputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[LInputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return SetSimulationInputsMessage[simulation_inputs]

    @staticmethod
    def subscribe_topic() -> str:
        return "set_inputs"

    async def handle(self, topic_prefix: str, context: MessageContext):
        context.simulation.update_simulation_inputs(self.inputs)
        await context.send(topic_prefix, SimulationInputMessage(inputs=self.inputs))


SIMULATION_HANDLERS = [
    SimulationPlayMessage,
    SimulationStepMessage,
    SimulationPauseMessage,
    SetSimulationInputsMessage,
]

CONTROLLER_HANDLERS = [
    ManualControlMessage,
    SetAutomationMessage,
    SetParametersMessage,
]
