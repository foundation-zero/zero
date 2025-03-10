from datetime import datetime, timedelta
from typing import TypeVar

from input_output.base import ThrsModel
from simulation.environmentals import Environmentals
from simulation.fmu import Fmu

ControlValues = TypeVar("ControlValues", bound=ThrsModel)
SensorValues = TypeVar("SensorValues", bound=ThrsModel)


class Executor(Fmu[ControlValues, SensorValues]):
    def __init__(
        self,
        fmu: Fmu[ControlValues, SensorValues],
        environmentals: Environmentals,
        start: datetime,
        stop: datetime,
        tick_duration: timedelta,
    ):
        self._fmu = fmu
        self._environmentals = environmentals
        self._tick_duration = tick_duration
        self._time = start
        self._stop = stop

    def run(self):
        while (self._time < self._stop) if self._stop else True:
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
