from abc import abstractmethod
from datetime import datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field

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
type PlaybackRate = Annotated[float, Field(ge=0.25, le=10)]


class SimulationStatusMessage(OutgoingMessage):
    mode: str
    status: SimulationStatus
    control_modules: list[str]
    simulation_time: datetime
    # Defaults, so a status from before these fields still reads.
    playback_rate: PlaybackRate = 1.0
    pause_at: datetime | None = None

    @staticmethod
    def subscribe_topic() -> str:
        return "status"


class SimulationStatusSetMessage(IncomingMessage):
    """Pause now, run at the playback rate, or step as fast as possible; running and
    stepping until pause_at, if it is later than the simulation time."""

    status: SimulationStatus
    playback_rate: PlaybackRate = 1.0
    # Aware, as the simulation clock is: comparing a naive one with it would raise.
    pause_at: AwareDatetime | None = None

    @staticmethod
    def subscribe_topic() -> str:
        return "status/set"
