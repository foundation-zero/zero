from dataclasses import dataclass
from datetime import datetime, timedelta
from classes.control import Control
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
    simulation_inputs: SimulationInputs
    start_time: datetime = datetime.now()
    tick_duration: timedelta = timedelta(seconds=1)
    solver_step_size: timedelta = timedelta(seconds=0.001)


class Simulator:
    def __init__(self, model: SimulatorModel):
        self._model = model
        self._executor = SimulationExecutor(
            IoMapping(
                Fmu(model.fmu_path, model.solver_step_size),
                model.sensor_values_cls,
                model.simulation_outputs_cls,
            ),
            model.simulation_inputs,
            model.start_time,
            model.tick_duration,
        )
        self._interfacer = Cycler(model.control, self._executor)

    async def run(self, n_ticks: int):
        collector = PolarsCollector()
        await self._interfacer.run(n_ticks, collector)
        self._result = collector.result()
        return self._result

    @property
    def result(self):
        return self._result
