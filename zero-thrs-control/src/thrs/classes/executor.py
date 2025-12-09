from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from thrs.input_output.base import SimulationInputs, ThrsValues


@dataclass
class ExecutionResult[S]:
    timestamp: datetime
    sensor_values: S


@dataclass
class SimulationExecutionResult[
    S: ThrsValues,
    C: ThrsValues,
    I: SimulationInputs,
    O: ThrsValues,
](ExecutionResult[S]):
    control_values: C
    simulation_outputs: O
    simulation_inputs: I
    raw: dict[str, Any]


class Executor[S, C](Protocol):
    async def start(self): ...
    async def tick(self, control_values: C) -> ExecutionResult[S]: ...

    @property
    def start_time(self) -> datetime: ...

    def time(self) -> datetime: ...
