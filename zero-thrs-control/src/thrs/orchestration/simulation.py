import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from types import TracebackType
from typing import Any, Self

from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.orchestration.module import ModuleClassMap
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import CombinedIoMapping, IoMapping, ThrsModelIoMapping

logger = logging.getLogger(__name__)


@dataclass
class SimulationResult[
    S: ThrsValues,
    C: ThrsValues,
    I: SimulationInputs,
    O: ThrsValues,
]:
    timestamp: datetime
    sensor_values: S
    control_values: C
    simulation_outputs: O
    simulation_inputs: I
    raw: dict[str, Any]


class Simulation[
    S,
    C,
    I: SimulationInputs,
    O: SimulationValues,
]:
    def __init__(
        self,
        sensor_values_clss: ModuleClassMap | type[ThrsValues],
        simulation_outputs_cls: type[O],
        fmu: Fmu,
        simulation_inputs: I,
        start_time: datetime,
        tick_duration: timedelta,
    ):
        self._start_time = start_time
        self._ticks = 0
        self._tick_duration = tick_duration
        self._simulation_inputs = simulation_inputs
        self._simulation_outputs_cls = simulation_outputs_cls
        self._fmu = fmu
        self._io_mapping: IoMapping = (
            CombinedIoMapping(sensor_values_clss, simulation_outputs_cls)  # type: ignore
            if isinstance(sensor_values_clss, dict)
            else ThrsModelIoMapping(sensor_values_clss, simulation_outputs_cls)  # type: ignore
        )

    def __enter__(self) -> Self:
        self._fmu.__enter__()
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return self._fmu.__exit__(type_, value, traceback)

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def tick_duration(self) -> timedelta:
        return self._tick_duration

    def time(self):
        return self._start_time + self._ticks * self._tick_duration

    def tick(self, control_values: C) -> SimulationResult[S, C, I, O]:
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
        )

    def update_simulation_inputs(self, simulation_inputs: I):
        self._simulation_inputs = simulation_inputs

    @property
    def inputs_cls(self) -> type[I]:
        return type(self._simulation_inputs)

    @property
    def simulation_inputs(self) -> I:
        return self._simulation_inputs

    @property
    def outputs_cls(self) -> type[O]:
        return self._simulation_outputs_cls
