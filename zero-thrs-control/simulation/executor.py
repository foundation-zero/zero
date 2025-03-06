from datetime import datetime, timedelta

from input_output.base import ThrsModel
from simulation.environmentals import Environmentals
from simulation.fmu import Fmu


class Executor:
    def __init__(
        self,
        fmu: Fmu,
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

    def set_control_values(self, control_values: ThrsModel):
        self._last_control_values = control_values
