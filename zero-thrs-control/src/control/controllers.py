from typing import cast

from simple_pid import PID

from input_output.definitions.units import Celsius, Ratio


class HeatDumpController:
    def __init__(self, setpoint: Celsius):
        self._pid = PID(
            -1, 0, 0, setpoint=setpoint, sample_time=0.1, output_limits=(0, 1)
        )

    def __call__(self, temperature: Celsius) -> Ratio:
        return cast(
            Ratio, self._pid(temperature)
        )  # Can safely cast since PID always returns a number except when auto_mode = False and there is no last_output available


class HeatSupplyController:
    def __init__(self, setpoint: Celsius):
        self._pid = PID(
            -1, 0, 0, setpoint=setpoint, sample_time=0.1, output_limits=(0, 1)
        )

    def __call__(self, temperature: Celsius) -> Ratio:
        return cast(Ratio, self._pid(temperature))  # See above
