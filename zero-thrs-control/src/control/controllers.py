from datetime import datetime
from typing import cast
from simple_pid import PID

from input_output.definitions.units import Celsius, LMin, Ratio


class _Controller[ValueUnit: float, SetpointUnit: float]:
    TUNING = (0, 0, 0)
    OUTPUT_LIMITS = (0, 1)

    def __init__(self, initial: ValueUnit, setpoint: SetpointUnit):
        kp, ki, kd = self.TUNING
        self._pid = PID(
            kp,
            ki,
            kd,
            setpoint=setpoint,
            sample_time=0.1,
            output_limits=self.OUTPUT_LIMITS,
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


    @property
    def setpoint(self) -> SetpointUnit:
        return cast(SetpointUnit, self._pid.setpoint)

    @setpoint.setter
    def setpoint(self, value: SetpointUnit):
        self._pid.setpoint = value

    def __call__(self, measurement: SetpointUnit, time: datetime) -> ValueUnit:
        self._pid.time_fn = lambda: time.timestamp()
        pid_result = cast(ValueUnit | None, self._pid(measurement))
        return pid_result if pid_result is not None else self._initial


class _HeatController(_Controller[Ratio, Celsius]):
    TUNING = (-0.1, -0.01, 0)
    OUTPUT_LIMITS = (0, 1)


class HeatDumpController(_HeatController):
    pass

class InvertedHeatDumpController(_HeatController):
    TUNING = (0.1, 0.01, 0)

class HeatSupplyController(_HeatController):
    pass


class PumpFlowController(_Controller[Ratio, LMin]):
    TUNING = (0.0, 0.002, 0)
    OUTPUT_LIMITS = (0, 1.0)
