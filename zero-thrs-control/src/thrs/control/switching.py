from typing import Literal

from thrs.classes.control import Control
from thrs.control.manual import ManualControl
from thrs.input_output.base import ThrsValues


class SwitchingControllerValues[M: ThrsValues](ThrsValues):
    automatic_mode: M | None

    @property
    def automatic(self) -> bool:
        return self.automatic_mode is not None


class SwitchingControl[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    ControlParameters: ThrsValues,
    ControllerValues: ThrsValues,
](
    Control[
        SensorValues,
        ControlValues,
        ControlParameters,
        SwitchingControllerValues[ControllerValues],
    ]
):
    def __init__(
        self,
        manual: ManualControl[SensorValues, ControlValues],
        automatic: Control[
            SensorValues, ControlValues, ControlParameters, ControllerValues
        ],
    ):
        self._manual_control = manual
        self._automatic_control = automatic
        self._mode: Literal["manual", "automatic"] = "manual"

    def initial(
        self,
    ) -> tuple[ControlValues, SwitchingControllerValues[ControllerValues]]:
        return (
            self._manual_control.initial()[0],
            SwitchingControllerValues(automatic_mode=None),
        )

    def control(
        self, sensor_values: SensorValues
    ) -> tuple[ControlValues, SwitchingControllerValues[ControllerValues]]:
        if self._mode == "manual":
            control_values, _ = self._manual_control.control(sensor_values)
            controller_values = SwitchingControllerValues(automatic_mode=None)
        else:
            control_values, controller_values = self._automatic_control.control(
                sensor_values
            )
            controller_values = SwitchingControllerValues(
                automatic_mode=controller_values
            )

        return control_values, controller_values

    def switch_mode(self, mode: Literal["manual", "automatic"]):
        self._mode = mode

    @property
    def parameters(self) -> ControlParameters:
        return self._automatic_control.parameters

    def update_parameters(self, parameters: ControlParameters):
        self._automatic_control.update_parameters(parameters)

    @staticmethod
    def modes() -> list[str]:
        return ["manual", "automatic"]

    @property
    def automatic(self) -> bool:
        return self._mode == "automatic"

    def manual_controls(self, values: ControlValues):
        self._manual_control.manual_controls(values)
