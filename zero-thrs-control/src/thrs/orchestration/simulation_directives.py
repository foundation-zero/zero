from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import Field

from thrs.control.switching import SwitchingControlMode
from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.orchestration.mqtt import (
    IncomingMessage,
    IncomingModuleMessage,
    MessageContext,
    OutgoingMessage,
)


class SimulationStatusMessage(OutgoingMessage):
    mode: str
    status: Literal["available", "running", "stepping"]
    control_modules: list[str]
    simulation_time: datetime

    @staticmethod
    def subscribe_topic() -> str:
        return "simulation/status"

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
        return "simulation/inputs"

    @staticmethod
    def retained() -> bool:
        return True


OUTGOING_MESSAGES = [
    SimulationStatusMessage,
    ControlModeMessage,
    ParametersMessage,
    SimulationInputMessage,
]


class SimulationCtrlMessage(IncomingMessage):
    async def handle(self, context: MessageContext):
        await context.cmds.put(self)


class PlayMessage(SimulationCtrlMessage):
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
        return "simulation/play"


class StepMessage(SimulationCtrlMessage):
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
        return "simulation/step"


class PauseMessage(SimulationCtrlMessage):
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
        return "simulation/pause"


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
        context: MessageContext[
            ThrsValues, ControlValues, ThrsValues, SimulationInputs, SimulationValues
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

    async def handle(self, context: MessageContext):
        context.control.set_automation_mode(self.module, self.enabled)
        await context.send(
            ControlModeMessage(
                module=self.module,
                mode=context.control.mode_for(self.module),
            )
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

    async def handle(self, context: MessageContext[Any, Any, Parameters, Any, Any]):
        context.control.update_parameters_for(self.module, self.parameters)
        await context.send(
            ParametersMessage(
                parameters=context.control.parameters.values[self.module],
                module=self.module,
            )
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
        return "simulation/set_inputs"

    async def handle(self, context: MessageContext):
        context.executor.update_simulation_inputs(self.inputs)
        await context.send(SimulationInputMessage(inputs=self.inputs))


DIRECTIVES = [
    PlayMessage,
    StepMessage,
    PauseMessage,
    ManualControlMessage,
    SetAutomationMessage,
    SetParametersMessage,
    SetSimulationInputsMessage,
]
