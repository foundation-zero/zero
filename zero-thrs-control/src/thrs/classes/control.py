from typing import Protocol

from thrs.input_output.base import ThrsValues


class Control[SensorValues, ControlValues, Parameters, ControlMode, ControllerState](
    Protocol
):
    def initial(self) -> tuple[ControlValues, ControllerState]: ...

    def control(
        self, sensor_values: SensorValues
    ) -> tuple[ControlValues, ControllerState]: ...

    @property
    def parameters(self) -> Parameters: ...

    @property
    def mode(self) -> ControlMode | None: ...

    def update_parameters(self, parameters: Parameters): ...


class ControlMode(ThrsValues):
    def __str__(self):
        values = [
            getattr(self, field_name)
            if isinstance(getattr(self, field_name), str)
            else f"{field_name}: {str(getattr(self, field_name))}"
            for field_name, field_info in type(self).model_fields.items()
        ]

        return ", ".join(values)
