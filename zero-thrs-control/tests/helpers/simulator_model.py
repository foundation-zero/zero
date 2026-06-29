from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

from thrs.classes.control import Control
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu


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
                self.sensor_values_cls,
                self.simulation_outputs_cls,
                fmu,
                self.simulation_inputs,
                self.start_time,
                self.tick_duration,
            )
