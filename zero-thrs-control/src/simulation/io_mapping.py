from datetime import datetime, timedelta

from input_output.base import SimulationInputs, ThrsModel
from input_output.fmu_mapping import build_inputs_for_fmu, build_outputs_from_fmu, extract_non_fmu_values
from simulation.fmu import Fmu

class IoMapping:
    def __init__(
        self,
        fmu: Fmu,
        sensor_values_cls: type[ThrsModel],
        simulation_outputs_cls: type[ThrsModel],
    ):
        self._fmu = fmu
        self._sensor_values_cls = sensor_values_cls
        self._simulation_outputs_cls = simulation_outputs_cls

    def tick(
        self,
        control_values: ThrsModel,
        simulation_inputs: SimulationInputs,
        time: datetime,
        tick_duration: timedelta,
    ) -> tuple[ThrsModel, ThrsModel, dict[str, float]]:

        fmu_outputs = self._fmu.tick(
            {
            **build_inputs_for_fmu(control_values),
            **build_inputs_for_fmu(simulation_inputs),
        },
            tick_duration,
        )
        sensor_extra_values = extract_non_fmu_values(simulation_inputs, self._sensor_values_cls)

        sensor_values, simulation_outputs = build_outputs_from_fmu(
            [self._sensor_values_cls, self._simulation_outputs_cls],
            fmu_outputs,
            time + tick_duration,
            sensor_extra_values,
        )
        return sensor_values, simulation_outputs, {**fmu_outputs, **build_inputs_for_fmu(simulation_inputs)}
