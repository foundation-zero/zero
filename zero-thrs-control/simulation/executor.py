from datetime import datetime, timedelta
from typing import Any, TypeVar

from pydantic import BaseModel

from input_output.base import ThrsModel
from simulation.fmu import Fmu
from simulation.input_output import SimulationInputs


# _units_strings = {"temperature": "C", "flow": "l_min", "pressure": "Bar"}

# def _model_fields_to_fmu_names(cls: type[ThrsModel]) -> list[str]:
#     return ["__".join(var) for var in [(component_str, var_str, _units_strings[var_str]) for component_str, component in cls.model_fields.items() for var_str in component.annotation.model_fields]]  # type: ignore


class Executor[
    ControlValues: ThrsModel,
    SensorValues: ThrsModel,
    Outputs: BaseModel,
    Inputs: SimulationInputs,
]:
    def __init__(
        self,
        fmu: Fmu,
        sensors_cls: type[SensorValues],
        simulation_outputs_cls: type[Outputs],
        controls_cls: type[ControlValues],
        simulation_inputs: Inputs,
        start: datetime,
        tick_duration: timedelta,
    ):
        self._fmu = fmu
        self._tick_duration = tick_duration
        self._sensors_cls = sensors_cls
        self._simulation_outputs_cls = simulation_outputs_cls
        self._controls_cls = controls_cls
        self._simulation_inputs = simulation_inputs
        self._time = start
        self._last_sensor_values, self._last_simulation_outputs = (
            self.process_fmu_outputs(self._fmu._initial_outputs)
        )

    def construct_fmu_inputs(
        self, control_values: ControlValues, last_simulation_inputs: Inputs
    ) -> dict[str, Any]:
        # TODO: Need to flatten control values, rename keys to match fmu inputs, then pass dict
        return {**control_values.model_dump(), **last_simulation_inputs.model_dump()}
        # TODO: perhaps better to distinguish between selected and non-selected simulation inputs...

    def process_fmu_outputs(
        self, outputs: dict[str, Any]
    ) -> tuple[SensorValues, Outputs]:
        # TODO: need construct SensorValues and SimulationOutputs objects from fmu outputs dict. Something similar to modelbuilder
        return self._sensors_cls(**outputs), self._simulation_outputs_cls(**outputs)

    def tick(self, control_values: ControlValues):
        self._last_control_values = control_values
        self._last_simulation_inputs = self._simulation_inputs.get_values_at_time(
            self._time
        )
        fmu_outputs = self._fmu.tick(
            self.construct_fmu_inputs(
                self._last_control_values, self._last_simulation_inputs
            ),
            self._tick_duration,
        )

        self._last_sensor_values, self._last_simulation_outputs = (
            self.process_fmu_outputs(fmu_outputs)
        )

        self._time += self._tick_duration

        return self._last_sensor_values, self._last_simulation_outputs

    @property
    def last_control_values(self) -> ControlValues:
        return self._last_control_values

    @property
    def time(self) -> datetime:
        return self._time

    @property
    def last_sensor_values(self) -> SensorValues:
        return self._last_sensor_values

    @property
    def last_simulation_outputs(self) -> Outputs:
        return self._last_simulation_outputs

    @property
    def last_simulation_inputs(self) -> Inputs:
        return self._last_simulation_inputs
