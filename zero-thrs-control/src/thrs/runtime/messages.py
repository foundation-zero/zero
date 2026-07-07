from abc import abstractmethod
from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from thrs.input_output.base import ThrsValues


class IncomingMessage(ThrsValues):
    @staticmethod
    @abstractmethod
    def subscribe_topic() -> str: ...


class OutgoingMessage(ThrsValues):
    @staticmethod
    @abstractmethod
    def subscribe_topic() -> str: ...


type SimulationStatus = Literal["available", "running", "stepping"]


class SimulationStatusMessage(OutgoingMessage):
    mode: str
    status: SimulationStatus
    control_modules: list[str]
    simulation_time: datetime

    @staticmethod
    def subscribe_topic() -> str:
        return "status"


class PlayMessage(IncomingMessage):
    playback_rate: Annotated[float, Field(ge=0.25, le=10)] = 1.0

    @staticmethod
    def subscribe_topic() -> str:
        return "play"


class StepMessage(IncomingMessage):
    seconds: Annotated[float, Field(ge=0)]

    @staticmethod
    def subscribe_topic() -> str:
        return "step"


class PauseMessage(IncomingMessage):
    @staticmethod
    def subscribe_topic() -> str:
        return "pause"
