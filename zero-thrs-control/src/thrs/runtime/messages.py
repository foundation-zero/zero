from abc import abstractmethod
from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues


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
