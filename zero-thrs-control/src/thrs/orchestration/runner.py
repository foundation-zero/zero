import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

from thrs.classes.control import Control
from thrs.control.base import ModuleDescription
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.collector import Collector
from thrs.orchestration.connector import Connector, ExecutionResult
from thrs.orchestration.module import CombinedModule
from thrs.orchestration.simulation import Simulation, SimulationResult
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping, flatten_model_values


@dataclass
class SimulatorModel:
    fmu_path: str
    sensor_values_cls: type[ThrsValues]
    control_values_cls: type[ThrsValues]
    simulation_outputs_cls: type[SimulationValues]
    control_cls: type[Control]
    alarms: BaseAlarms
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)

    @contextmanager
    def simulation(self):
        with Fmu(self.fmu_path) as fmu:
            yield Simulation(
                ThrsModelIoMapping(
                    self.sensor_values_cls,
                    self.simulation_outputs_cls,
                ),
                fmu,
                self.simulation_inputs,
                self.start_time,
                self.tick_duration,
            )


@dataclass
class ModuleSimulatorModel:
    fmu_path: str
    module: CombinedModule
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)

    @contextmanager
    def simulation(self):
        with Fmu(self.fmu_path) as fmu:
            yield Simulation(
                self.module.io_mapping(),
                fmu,
                self.simulation_inputs,
                self.start_time,
                self.tick_duration,
            )


class Runner[S: ThrsValues, C: ThrsValues, P: ThrsValues, M: ThrsValues]:
    """Runs a module for a number of ticks

    Allows for a pluggable collector to collect execution results during the run.
    """

    last_tick_result: ExecutionResult | None  # TODO: Remove this, only used in tests

    def __init__(
        self,
        connector: Connector[S, C],
        control: Control[S, C, P, M],
        alarms: BaseAlarms[S, C, P],
    ):
        self._control = control
        self._connector = connector
        self._alarms = alarms
        self._control_values = self._control.initial().values
        self.last_tick_result = None

    @staticmethod
    def from_module(
        module: ModuleDescription[S, C, P, M] | CombinedModule,
        initial_control_parameters: P | CombinedValues,
        connector: Connector[S, C],
    ) -> "Runner":
        return Runner(
            connector,
            module.control(initial_control_parameters, connector.time),  # type:ignore
            module.alarms(),  # type:ignore
        )

    async def run(self, n_ticks: int, collector: Collector | None = None) -> None:
        result = None
        for _ in range(n_ticks):
            result = await self._connector.tick(self._control_values)
            if isinstance(result, SimulationResult) and collector is not None:
                collector.collect(
                    {
                        **flatten_model_values(result.sensor_values, fmu_only=False),
                        **flatten_model_values(result.control_values, fmu_only=False),
                        **flatten_model_values(
                            result.simulation_outputs, fmu_only=False
                        ),
                        **flatten_model_values(
                            result.simulation_inputs, fmu_only=False
                        ),
                    },
                    str(self._control.mode),
                    result.timestamp,
                )
            self._control_values = self._control.control(result.sensor_values).values
            alarms = self._alarms.check(
                result.sensor_values, self._control_values, self._control.parameters
            )
            if alarms:
                warnings.warn(
                    f"Alarms detected: {alarms}"
                )  # TODO: properly handle alarms
        self.last_tick_result = result
