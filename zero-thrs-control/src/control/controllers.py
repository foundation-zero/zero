from datetime import datetime
from typing import cast
from simple_pid import PID

from input_output.base import Stamped
from input_output.definitions.control import Valve
from input_output.definitions.units import Celsius, LMin, Ratio


class _Controller[ValueUnit: float, SetpointUnit: float]:
    TUNING = (0, 0, 0)
    OUTPUT_LIMITS = (0, 1)

    def __init__(
        self,
        initial: ValueUnit,
        setpoint: SetpointUnit,
        tuning: tuple[float, float, float] | None = None,
    ):
        kp, ki, kd = tuning or self.TUNING
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

    def enabled(self) -> bool:
        return self._pid.auto_mode

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


class _FlowController(_Controller[Ratio, LMin]):
    OUTPUT_LIMITS = (0, 1.0)


class FlowBalanceController:
    def __init__(self, valves: list[Valve]):
        self._controllers = [
            _FlowController(Valve.CLOSED, 0.0, (0.0, 0.002, 0)) for _ in valves
        ]
        self._valves = valves

    def set_actives(self, actives: list[bool]):
        for controller, active in zip(self._controllers, actives):
            if not controller.enabled() and active:
                controller.enable()
            elif controller.enabled() and not active:
                controller.disable()

    def set_setpoint(self, setpoint: LMin):
        for controller in self._controllers:
            controller.setpoint = setpoint

    def __call__(self, measurements: list[LMin], time: datetime):
        controller_values = [
            controller(measurement, time)
            for controller, measurement in zip(self._controllers, measurements)
        ]
        offset = 1 - max(*controller_values)
        for value, controller, valve in zip(
            controller_values, self._controllers, self._valves
        ):
            if controller.enabled():
                valve.setpoint = Stamped(value=value + offset, timestamp=time)
            else:
                valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=time)


class PumpFlowController(_FlowController):
    TUNING = (0.0, 0.002, 0)
