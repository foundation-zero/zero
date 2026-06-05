from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

from thrs.classes.control import Control
from thrs.classes.executor import Executor
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.collector import PolarsCollector
from thrs.orchestration.cycler import Cycler
from thrs.orchestration.executor import SimulationExecutor
from thrs.orchestration.module import CombinedModule
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping


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
    def __init__(self, executor: Executor, control: Control, alarms: BaseAlarms):
        self._executor = executor
        self._cycler = Cycler(
            control,
            self._executor,
            alarms,
        )

    @staticmethod
    def from_model(
        model: SimulatorModel | ModuleSimulatorModel, executor: Executor
    ) -> "Simulator":
        return Simulator(
            executor,
            model.control(executor),
            model.alarms,
        )

    async def run(self, n_ticks: int):
        collector = PolarsCollector()
        await self._cycler.run(n_ticks, collector)
        self._result = collector.result()
        return self._result

    @property
    def result(self):
        return self._result
