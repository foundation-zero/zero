from datetime import datetime, timedelta
from typing import TypeVar

from input_output.base import ThrsModel
from simulation.fmu import Fmu
from simulation.input_output import SimulationInputs

ControlValues = TypeVar("ControlValues", bound=ThrsModel)
SensorValues = TypeVar("SensorValues", bound=ThrsModel)


class Executor(Fmu[ControlValues, SensorValues]):
    def __init__(
        self,
        fmu: Fmu[ControlValues, SensorValues],
        simulation_inputs: SimulationInputs,
        start: datetime,
        stop: datetime,
        tick_duration: timedelta,
    ):
        self._fmu = fmu
        self._environmentals = simulation_inputs
        self._tick_duration = tick_duration
        self._time = start
        self._stop = stop
        self._last_sensor_values = self._fmu._initial_values

    def run(self):
        while self._time < self._stop:
            self._last_sensor_values = self._fmu.tick(
                self._last_control_values,
                self._environmentals.get_values_at_time(self._time),
                self._tick_duration,
            )
            self._time += self._tick_duration

    def set_control_values(self, control_values: ControlValues):
        self._last_control_values = control_values

    @property
    def time(self) -> datetime:
        return self._time

    @property
    def last_sensor_values(self) -> SensorValues:
        return self._last_sensor_values
