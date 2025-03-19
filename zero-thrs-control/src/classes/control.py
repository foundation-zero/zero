from typing import Protocol
from input_output.base import ThrsModel


class Control[S: ThrsModel, C: ThrsModel](Protocol):

    def initial(self) -> C: ...

    def control(self, sensor_values: S) -> C: ...
