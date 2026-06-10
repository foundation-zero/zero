import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

from thrs.classes.control import Control
from thrs.classes.executor import ExecutionResult, Executor
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.collector import Collector
from thrs.orchestration.executor import (
    SimulationExecutionResult,
    SimulationExecutor,
)
from thrs.orchestration.module import CombinedModule
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping, flatten_model_values


@dataclass
class SimulatorModel:
    fmu_path: str
    sensor_values_cls: type[ThrsValues]
    control_values_cls: type[ThrsValues]
    simulation_outputs_cls: type[SimulationValues]
    control_cls: type[Control]
    control_parameters: ThrsValues
    alarms: BaseAlarms
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)

    @contextmanager
    def executor(self):
        with Fmu(self.fmu_path) as fmu:
            yield SimulationExecutor(
                ThrsModelIoMapping(
                    self.sensor_values_cls,
                    self.simulation_outputs_cls,
                ),
                fmu,
                self.simulation_inputs,
                self.start_time,
                self.tick_duration,
            )

    def control(self, executor: Executor):
        return self.control_cls(self.control_parameters, executor.time)


@dataclass
class ModuleSimulatorModel:
    fmu_path: str
    module: CombinedModule
    control_parameters: CombinedValues
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)

    @contextmanager
    def executor(self):
        with Fmu(self.fmu_path) as fmu:
            yield SimulationExecutor(
                self.module.io_mapping(),
                fmu,
                self.simulation_inputs,
                self.start_time,
                self.tick_duration,
            )

    def control(self, executor: Executor):
        return self.module.control(self.control_parameters, executor.time)

    @property
    def alarms(self):
        return self.module.alarms()


class Simulator:
    last_tick_result: ExecutionResult | None  # TODO: Remove this, only used in tests

    def __init__(self, executor: Executor, control: Control, alarms: BaseAlarms):
        self._control = control
        self._executor = executor
        self._alarms = alarms
        self._control_values = self._control.initial().values
        self.last_tick_result = None

    @staticmethod
    def from_model(
        model: SimulatorModel | ModuleSimulatorModel, executor: Executor
    ) -> "Simulator":
        return Simulator(
            executor,
            model.control(executor),
            model.alarms,
        )

    async def run(self, n_ticks: int, collector: Collector | None = None) -> None:
        result = None
        for _ in range(n_ticks):
            result = await self._executor.tick(self._control_values)
            if isinstance(result, SimulationExecutionResult) and collector is not None:
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
