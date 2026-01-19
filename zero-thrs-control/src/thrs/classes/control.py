from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol


@dataclass
class ControlResult[C]:
    timestamp: datetime
    values: C


class Control[S, C, P, M](Protocol):
    def __init__(self, parameters: P, time_fn: Callable[[], datetime]): ...

    def initial(self) -> ControlResult[C]: ...

    def control(self, sensor_values: S) -> ControlResult[C]: ...

    @property
    def parameters(self) -> P: ...

    @property
    def mode(self) -> M | None: ...

    def update_parameters(self, parameters: P): ...
