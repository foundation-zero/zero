from typing import cast

from simple_pid import PID

from input_output.units import Celsius, Ratio


class HeatDumpController:
    def __init__(self, setpoint: Celsius):
        self._pid = PID(
            1, 0, 0, setpoint=setpoint, sample_time=0.1, output_limits=(0, 1)
        )

    def __call__(self, temperature: Celsius) -> Ratio:
        return cast(Ratio, self._pid(temperature))
