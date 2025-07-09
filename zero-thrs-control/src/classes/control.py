from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from input_output.base import ThrsModel


@dataclass
class ControlResult[C: ThrsModel]:
    timestamp: datetime
    values: C


class Control[S: ThrsModel, C: ThrsModel, P: ThrsModel](Protocol):

    def initial(self, time: datetime) -> ControlResult[C]: ...

    def control(self, sensor_values: S, time: datetime) -> ControlResult[C]: ...

    @property
    def parameters(self) -> P: ...

    @property
    def modes(self) -> list[str]: ...

    @property
    def mode(self) -> str | None: ...
