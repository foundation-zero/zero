from datetime import datetime
from typing import Callable, Protocol

from thrs.input_output.base import ThrsValues


class Control[S, C, P, M](Protocol):
    def __init__(self, parameters: P, time_fn: Callable[[], datetime]): ...

    def initial(self) -> C: ...

    def control(self, sensor_values: S) -> C: ...

    @property
    def parameters(self) -> P: ...

    @property
    def mode(self) -> M | None: ...

    def update_parameters(self, parameters: P): ...


class ControlMode(ThrsValues):
    def __str__(self):
        values = [
            getattr(self, field_name)
            if isinstance(getattr(self, field_name), str)
            else f"{field_name}: {str(getattr(self, field_name))}"
            for field_name, field_info in type(self).model_fields.items()
        ]

        return ", ".join(values)
