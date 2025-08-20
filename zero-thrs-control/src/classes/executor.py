from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from input_output.base import SimulationInputs, ThrsModel


@dataclass
class ExecutionResult[S: ThrsModel]:
    timestamp: datetime
    sensor_values: S


@dataclass
class SimulationExecutionResult[S: ThrsModel, I: SimulationInputs, O: ThrsModel](
    ExecutionResult[S]
):
    simulation_outputs: O
    simulation_inputs: I
    raw: dict[str, Any]


class Executor[S: ThrsModel, C: ThrsModel](Protocol):
    async def start(self): ...
    async def tick(self, control_values: C) -> ExecutionResult[S]: ...

    @property
    def start_time(self) -> datetime: ...
