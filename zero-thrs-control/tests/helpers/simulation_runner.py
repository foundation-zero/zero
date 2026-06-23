import warnings
from typing import Callable

from tests.helpers.collector import Collector
from thrs.classes.control import Control
from thrs.control.base import ModuleDescription
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import CombinedValues, SimulationInputs, ThrsValues
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.orchestration.module import CombinedModule
from thrs.orchestration.simulation import Simulation, SimulationResult
from thrs.simulation.io_mapping import flatten_model_values


class SimulationTestRunner[
    S: ThrsValues,
    C: ThrsValues,
    I: SimulationInputs,
    O: ThrsValues,
    P: ThrsValues,
    M: ThrsValues,
]:
    """Runs a module for a number of ticks

    Allows for a pluggable collector to collect execution results during the run.
    """

    def __init__(
        self,
        simulation: Simulation[S, C, I, O],
        control: Control[S, C, P, M],
        alarms: BaseAlarms,
    ):
        self._control = control
        self._simulation = simulation
        self._alarms = alarms
        self._control_values = self._control.initial()

    @staticmethod
    def from_module(
        module: ModuleDescription | CombinedModule,
        initial_control_parameters: ThrsValues | CombinedValues,
        simulation: Simulation[S, C, I, O],
    ) -> "SimulationTestRunner":
        return SimulationTestRunner(
            simulation,
            module.control(initial_control_parameters, simulation.time),  # type:ignore
            module.alarms(),
        )

    def tick(
        self, collector: Collector | None = None
    ) -> tuple[SimulationResult | None, C]:
        result = self._simulation.tick(self._control_values)
        if isinstance(result, SimulationResult) and collector is not None:
            collector.collect(  # TODO: fix the fmu key mapping here, this is just a quick fix to get the tests working
                {
                    **flatten_model_values(
                        result.sensor_values,
                        build_fmu_key_mapping(
                            type(result.sensor_values), fmu_only=False
                        ),
                    ),
                    **flatten_model_values(
                        result.control_values,
                        build_fmu_key_mapping(
                            type(result.control_values), fmu_only=False
                        ),
                    ),
                    **flatten_model_values(
                        result.simulation_outputs,
                        build_fmu_key_mapping(
                            type(result.simulation_outputs), fmu_only=False
                        ),
                    ),
                    **flatten_model_values(
                        result.simulation_inputs,
                        build_fmu_key_mapping(
                            type(result.simulation_inputs), fmu_only=False
                        ),
                    ),
                },
                str(self._control.mode),
                result.timestamp,
            )
        self._control_values = self._control.control(result.sensor_values)
        alarms = self._alarms.check(
            result.sensor_values, self._control_values, self._control.parameters
        )
        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")  # TODO: properly handle alarms
        self.last_tick_result = result
        return self.last_tick_result, self._control_values

    def run(
        self, n_ticks: int, collector: Collector | None = None
    ) -> tuple[SimulationResult | None, C]:
        for _ in range(n_ticks):
            self.tick(collector)
        return self.last_tick_result, self._control_values

    def run_until(
        self,
        condition: Callable[[SimulationResult | None, C], bool],
        collector: Collector | None = None,
    ) -> tuple[SimulationResult | None, C]:
        while not condition(self.last_tick_result, self._control_values):
            self.tick(collector)
        return self.last_tick_result, self._control_values
