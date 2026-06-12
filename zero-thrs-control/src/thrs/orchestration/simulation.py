import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal

from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.orchestration.module import ModuleClassMap
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import CombinedIoMapping, IoMapping, ThrsModelIoMapping

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult[S]:
    timestamp: datetime
    sensor_values: S


@dataclass
class SimulationResult[
    S,
    C,
    I: SimulationInputs,
    O: SimulationValues,
](ExecutionResult[S]):
    control_values: C
    simulation_outputs: O
    simulation_inputs: I
    raw: dict[str, Any]
    fmu: Fmu

    def read_fmu_value(self, name: str) -> Any:
        variable = next(
            (
                variable
                for variable in self.fmu._model_description.modelVariables
                if name == variable.name
            ),
            None,
        )
        if variable is None:
            raise ValueError(f"Variable '{name}' not found in FMU model.")
        return self.fmu._fmu_instance.getReal([variable.valueReference])[0]  # type: ignore

    def find_fmu_variables(
        self, name: str, match: Literal["include", "startswith"] = "include"
    ) -> list[Any]:
        return [
            variable
            for variable in self.fmu._model_description.modelVariables
            if (
                name in variable.name
                if match == "include"
                else variable.name.startswith(name)
            )
        ]

    def summarize_fmu_values(self, name: str) -> dict[str, Any]:
        variables = self.find_fmu_variables(f"{name}.summary", match="startswith")
        return {
            variable.name: self.read_fmu_value(variable.name) for variable in variables
        }


class Simulation[
    S,
    C,
    I: SimulationInputs,
    O: SimulationValues,
]:
    def __init__(
        self,
        sensor_values_clss: ModuleClassMap | type[ThrsValues],
        simulation_outputs_cls: type[SimulationValues],
        fmu: Fmu,
        simulation_inputs: I,
        start_time: datetime,
        tick_duration: timedelta,
    ):
        self._start_time = start_time
        self._ticks = 0
        self._tick_duration = tick_duration
        self._simulation_inputs = simulation_inputs
        self._fmu = fmu
        self._io_mapping: IoMapping = (
            CombinedIoMapping(sensor_values_clss, simulation_outputs_cls)  # type: ignore
            if isinstance(sensor_values_clss, dict)
            else ThrsModelIoMapping(sensor_values_clss, simulation_outputs_cls)  # type: ignore
        )

    async def start(self):
        pass

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def tick_duration(self) -> timedelta:
        return self._tick_duration

    def time(self):
        return self._start_time + self._ticks * self._tick_duration

    async def tick(self, control_values: C) -> SimulationResult[S, C, I, O]:
        logging.debug("Running simulation tick")
        time = self.time()

        simulation_inputs = self._simulation_inputs.get_values_at_time(time)
        fmu_inputs = self._io_mapping.generate_inputs(control_values, simulation_inputs)
        fmu_outputs = self._fmu.tick(fmu_inputs, self._tick_duration)
        sensor_values, simulation_outputs, raw = self._io_mapping.construct_outputs(
            fmu_inputs, fmu_outputs, simulation_inputs, time + self._tick_duration
        )

        self._ticks += 1
        return SimulationResult(
            timestamp=time,
            sensor_values=sensor_values,
            control_values=control_values,
            simulation_outputs=simulation_outputs,
            simulation_inputs=simulation_inputs,
            raw=raw,
            fmu=self._fmu,
        )

    def update_simulation_inputs(self, simulation_inputs: I):
        self._simulation_inputs = simulation_inputs
