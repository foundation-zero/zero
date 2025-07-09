from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from classes.control import Control
from classes.executor import Executor
from input_output.alarms import BaseAlarms
from input_output.base import SimulationInputs, ThrsModel
from orchestration.collector import PolarsCollector
from orchestration.executor import SimulationExecutor
from orchestration.cycler import Cycler
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping


@dataclass
class SimulatorModel:
    fmu_path: str
    sensor_values_cls: type[ThrsModel]
    control_values_cls: type[ThrsModel]
    simulation_outputs_cls: type[ThrsModel]
    control: Control
    alarms: BaseAlarms
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)
    solver_step_size: timedelta = timedelta(seconds=0.001)

    @contextmanager
    def executor(self):
        with Fmu(self.fmu_path) as fmu:
            yield SimulationExecutor(
                IoMapping(
                    fmu,
                    self.sensor_values_cls,
                    self.simulation_outputs_cls,
                ),
                self.simulation_inputs,
                self.start_time,
                self.tick_duration,
            )


class Simulator:
    def __init__(self, model: SimulatorModel, executor: Executor):
        self._model = model
        self._executor = executor
        self._cycler = Cycler(model.control, self._executor, model.alarms)

    async def run(self, n_ticks: int):
        collector = PolarsCollector()
        await self._cycler.run(n_ticks, collector)
        self._result = collector.result()
        return self._result

    @property
    def result(self):
        return self._result
