from simple_pid import PID

from input_output.definitions.units import Celsius, Ratio


class _Controller:

    def __init__(self, initial: Ratio, setpoint: Celsius):
        self._pid = PID(
            -1,
            0,
            0,
            setpoint=setpoint,
            sample_time=0.1,
            output_limits=(0, 1),
            auto_mode=False,
        )
        self._initial = initial

    def enable(self):
        if self._pid.auto_mode:
            raise Exception("PID is already enabled")
        self._pid.auto_mode = True

    def disable(self):
        if not self._pid.auto_mode:
            raise Exception("PID is already disabled")
        self._pid.auto_mode = False

    def __call__(self, temperature: Celsius) -> Ratio:
        pid_result = self._pid(temperature)
        return pid_result if pid_result is not None else self._initial


class HeatDumpController(_Controller):
    pass


class HeatSupplyController(_Controller):
    pass
