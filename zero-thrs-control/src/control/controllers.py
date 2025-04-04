from simple_pid import PID

from input_output.definitions.units import Celsius, Ratio


class _Controller:
    TUNING = (0, 0, 0)

    def __init__(self, initial: Ratio, setpoint: Celsius):
        kp, ki, kd = self.TUNING
        self._pid = PID(
            kp,
            ki,
            kd,
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


class _HeatController(_Controller):
    TUNING = (-1, 0, 0)


class HeatDumpController(_HeatController):
    pass


class HeatSupplyController(_HeatController):
    pass


class PumpFlowController(_Controller):
    TUNING = (1, 0.1, 0)
