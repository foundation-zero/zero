from typing import Callable, cast

from tests.helpers.collector import Collector
from thrs.classes.control import Control
from thrs.control.switching import AutomationMode
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.orchestration.comms import ControlChannels, SimulationChannels
from thrs.orchestration.module import Module, ModuleDescription
from thrs.orchestration.simulation import Simulation, SimulationModule
from thrs.simulation.io_mapping import flatten_model_values


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


class SimulationTestRunner[
    S: ThrsValues,
    C: ThrsValues,
    I: SimulationInputs,
    O: SimulationValues,
    P: ThrsValues,
    M: ThrsValues,
    CS: ThrsValues,
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
        self._simulation = simulation

        self._control_values, self._controller_state = control.initial()

        # Since we are not sending or receiving we use None as channels for simplicity
        self._control_module = Module(
            "test", control, alarms, cast(ControlChannels, None)
        )
        self._control_module._control.switch_mode(AutomationMode(mode="automatic"))
        self._simulation_module = SimulationModule(
            simulation, cast(SimulationChannels, None)
        )

    @staticmethod
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
    ) -> "SimulationTestRunner[S2, C2, I2, O2, P2, M2, CS2]":
        return SimulationTestRunner(
            simulation,
            module.control(initial_control_parameters, simulation.time),
            module.alarms(),
        )

    def tick(self, collector: Collector | None = None) -> tuple[S | None, C, CS]:
        result = self._simulation_module.execute_simulation_tick(self._control_values)

        if collector is not None:
            collector.collect(  # TODO: fix the fmu key mapping here, this is just a quick fix to get the tests working
                {
                    **_flatten_for_collector(result.sensor_values),
                    **_flatten_for_collector(result.control_values),
                    **_flatten_for_collector(self._controller_state),
                    **_flatten_for_collector(result.simulation_outputs),
                    **_flatten_for_collector(result.simulation_inputs),
                },
                str(self._control_module._control.mode),
                result.timestamp,
            )

        self._control_values, self._controller_state = (
            self._control_module.execute_control_tick(result.sensor_values)
        )

        return result.sensor_values, self._control_values, self._controller_state

    def run(
        self, n_ticks: int, collector: Collector | None = None
    ) -> tuple[S | None, C, CS]:
        result = (None, self._control_values, self._controller_state)
        for _ in range(n_ticks):
            result = self.tick(collector)
        return result

    def run_until(
        self,
        condition: Callable[[S | None, C, CS], bool],
        collector: Collector | None = None,
    ) -> tuple[S | None, C, CS]:
        result = self.tick(collector)
        while not condition(*result):
            result = self.tick(collector)
        return result
