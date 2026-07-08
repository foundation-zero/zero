import warnings
from typing import Callable, overload

from tests.helpers.collector import Collector
from thrs.classes.control import Control
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.orchestration.module import CombinedModule, ModuleDescription
from thrs.orchestration.simulation import Simulation, SimulationResult
from thrs.simulation.io_mapping import flatten_model_values


class SimulationTestRunner[
    S: ThrsValues | CombinedValues,
    C: ThrsValues | CombinedValues,
    I: SimulationInputs,
    O: SimulationValues,
    P: ThrsValues | CombinedValues,
    M,
    CS: ThrsValues | CombinedValues,
]:
    """Runs a module for a number of ticks

    Allows for a pluggable collector to collect execution results during the run.
    """

    def __init__(
        self,
        simulation: Simulation[S, C, I, O],
        control: Control[S, C, P, M, CS],
        alarms: BaseAlarms[S, C, P],
    ):
        self._control = control
        self._simulation = simulation
        self._alarms = alarms
        self._control_values, self._controller_state = self._control.initial()
        self.last_tick_result: SimulationResult | None = None

    @staticmethod
    @overload
    def from_module[
        S2: ThrsValues,
        C2: ThrsValues,
        I2: SimulationInputs,
        O2: SimulationValues,
        P2: ThrsValues,
        M2: ThrsValues,
        CS2: ThrsValues,
    ](
        module: ModuleDescription[S2, C2, P2, M2, CS2],
        initial_control_parameters: P2,
        simulation: Simulation[S2, C2, I2, O2],
    ) -> "SimulationTestRunner[S2, C2, I2, O2, P2, M2, CS2]": ...

    @staticmethod
    @overload
    def from_module[
        I2: SimulationInputs,
        O2: SimulationValues,
    ](
        module: CombinedModule,
        initial_control_parameters: CombinedValues,
        simulation: Simulation[CombinedValues, CombinedValues, I2, O2],
    ) -> "SimulationTestRunner[CombinedValues, CombinedValues, I2, O2, CombinedValues, CombinedValues, CombinedValues]": ...

    @staticmethod
    def from_module(
        module: ModuleDescription | CombinedModule,
        initial_control_parameters: ThrsValues | CombinedValues,
        simulation: Simulation,
    ) -> "SimulationTestRunner":
        if isinstance(module, CombinedModule):
            if not isinstance(initial_control_parameters, CombinedValues):
                raise TypeError(
                    "CombinedModule requires CombinedValues as initial parameters"
                )
            return SimulationTestRunner(
                simulation,
                module.control(initial_control_parameters, simulation.time),
                module.alarms(),
            )

        return SimulationTestRunner(
            simulation,
            module.control(initial_control_parameters, simulation.time),
            module.alarms(),
        )

    @staticmethod
    def _flatten_for_collector(values: ThrsValues | CombinedValues) -> dict[str, float]:
        if isinstance(values, CombinedValues):
            return {
                key: value
                for model in values.values.values()
                for key, value in flatten_model_values(
                    model,
                    build_fmu_key_mapping(type(model), fmu_only=False),
                ).items()
            }

        return flatten_model_values(
            values,
            build_fmu_key_mapping(type(values), fmu_only=False),
        )

    def tick(
        self, collector: Collector | None = None
    ) -> tuple[SimulationResult[S, C, I, O] | None, C, CS]:
        result = self._simulation.tick(self._control_values)
        if collector is not None:
            collector.collect(  # TODO: fix the fmu key mapping here, this is just a quick fix to get the tests working
                {
                    **SimulationTestRunner._flatten_for_collector(result.sensor_values),
                    **SimulationTestRunner._flatten_for_collector(
                        result.control_values
                    ),
                    **SimulationTestRunner._flatten_for_collector(
                        self._controller_state
                    ),
                    **SimulationTestRunner._flatten_for_collector(
                        result.simulation_outputs
                    ),
                    **SimulationTestRunner._flatten_for_collector(
                        result.simulation_inputs
                    ),
                },
                str(self._control.mode),
                result.timestamp,
            )
        self._control_values, self._controller_state = self._control.control(
            result.sensor_values
        )
        alarms = self._alarms.check(
            result.sensor_values, self._control_values, self._control.parameters
        )
        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")  # TODO: properly handle alarms
        self.last_tick_result = result
        return self.last_tick_result, self._control_values, self._controller_state

    def run(
        self, n_ticks: int, collector: Collector | None = None
    ) -> tuple[SimulationResult[S, C, I, O] | None, C, CS]:
        for _ in range(n_ticks):
            self.tick(collector)
        return self.last_tick_result, self._control_values, self._controller_state

    def run_until(
        self,
        condition: Callable[[SimulationResult[S, C, I, O] | None, C, CS], bool],
        collector: Collector | None = None,
    ) -> tuple[SimulationResult[S, C, I, O] | None, C, CS]:
        while not condition(
            self.last_tick_result, self._control_values, self._controller_state
        ):
            self.tick(collector)
        return self.last_tick_result, self._control_values, self._controller_state
