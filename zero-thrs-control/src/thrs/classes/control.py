from datetime import datetime
from typing import TYPE_CHECKING, Callable, Protocol


from thrs.input_output.base import ThrsValues

if TYPE_CHECKING:
    from thrs.classes.machine_state_logger import StateLogger


class Control[SensorValues, ControlValues, Parameters, ControlMode, ControllerState](
    Protocol
):
    def __init__(self, parameters: Parameters, time_fn: Callable[[], datetime]): ...

    def initial(self) -> tuple[ControlValues, ControllerState]: ...

    def control(
        self, sensor_values: SensorValues
    ) -> tuple[ControlValues, ControllerState]: ...

    @property
    def parameters(self) -> Parameters: ...

    _parameters: "P"

    @property
    def mode(self) -> ControlMode | None: ...

    def update_parameters(self, parameters: Parameters): ...

    state: str  # Set by transitions logic
    state_logger: "StateLogger"


class ControlMode(ThrsValues):
    def __str__(self):
        values = [
            getattr(self, field_name)
            if isinstance(getattr(self, field_name), str)
            else f"{field_name}: {str(getattr(self, field_name))}"
            for field_name, field_info in type(self).model_fields.items()
        ]

        return ", ".join(values)
