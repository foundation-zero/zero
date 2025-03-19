from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from input_output.base import ThrsModel


@dataclass
class ExecutionResult[S: ThrsModel]:
    timestamp: datetime
    sensor_values: S


@dataclass
class SimulationExecutionResult(ExecutionResult):
    simulation_outputs: ThrsModel
    raw: dict[str, float]


class Executor[S: ThrsModel, C: ThrsModel](Protocol):
    def __init__(self, start_time):
        self._start_time: datetime

    async def start(self): ...
    async def tick(self, control_values: C) -> ExecutionResult[S]: ...
