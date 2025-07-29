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
        output_limits: tuple[float, float] | None = None,
    ):
        kp, ki, kd = tuning or self.TUNING
        self.output_limits = output_limits or self.OUTPUT_LIMITS
        self._pid = PID(
            kp,
            ki,
            kd,
            setpoint=setpoint,
            sample_time=0.1,
            output_limits=self.output_limits,
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


class FlowBasedTemperatureController(_Controller[LMin, Celsius]):
    TUNING = (-.001, -0.0001, 0)


class HeatDumpController(_Controller[Ratio, Celsius]):
    TUNING = (-0.1, -0.01, 0)
    OUTPUT_LIMITS = (0, 1.0)


class InvertedHeatDumpController(_Controller[Ratio, Celsius]):
    TUNING = (0.1, 0.01, 0)
    OUTPUT_LIMITS = (0, 1.0)


class MixingValveController(_Controller[Ratio, Celsius]):
    TUNING = (-0.001, -0.001, 0.1)
    OUTPUT_LIMITS = (0, 1.0)


class _FlowController(_Controller[Ratio, LMin]):
    TUNING = (0.001, 0.001, 0)
    OUTPUT_LIMITS = (0, 1.0)


class FlowBalanceController:
    def __init__(self, valves: list[Valve], close_when_disabled: bool = True):
        self._controllers = [
            _FlowController(Valve.CLOSED, 0.0, (0.0, 0.002, 0)) for _ in valves
        ]
        self._valves = valves
        self._close_when_disabled = close_when_disabled

    def set_actives(self, actives: list[bool]):
        if len(actives) != len(self._controllers):
            raise ValueError("Actives length must match valves length")
        for controller, active in zip(self._controllers, actives):
            if not controller.enabled() and active:
                controller.enable()
            elif controller.enabled() and not active:
                controller.disable()

    def get_actives(self) -> list[bool]:
        return [controller.enabled() for controller in self._controllers]

    def set_setpoint(self, setpoint: LMin):
        for controller in self._controllers:
            controller.setpoint = setpoint

    def set_setpoints(self, setpoints: list[LMin]):
        if len(setpoints) != len(self._controllers):
            raise ValueError("Setpoints length must match valves length")

        for controller, setpoint in zip(self._controllers, setpoints):
            controller.setpoint = setpoint

    def __call__(self, measurements: list[LMin], time: datetime):
        if len(measurements) != len(self._controllers):
            raise ValueError("Measurements length must match valves length")

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
            elif self._close_when_disabled:
                valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=time)


class FlowDistributionController:
    def __init__(self, valves: list[Valve]):
        self._flow_balance_controller = FlowBalanceController(
            valves, close_when_disabled=False
        )

    def set_actives(self, actives: list[bool]):
        self._flow_balance_controller.set_actives(actives)

    def set_ratios(self, ratios: list[Ratio | None]):
        if len(ratios) != (len(self._flow_balance_controller._controllers)):
            raise ValueError("Ratios length must be valves length")
        if sum(ratio for ratio in ratios if ratio is not None) != 1.0:
            raise ValueError("Ratios must sum to 1.0")

        self._ratios = ratios

    def __call__(self, measurements: list[LMin], time: datetime):
        if len(measurements) != len(self._flow_balance_controller._controllers):
            raise ValueError("Measurements length must match valves length")
        if any(
            (
                True
                for ratio, active in zip(
                    self._ratios, self._flow_balance_controller.get_actives()
                )
                if (ratio is None and active) or (ratio is not None and not active)
            )
        ):
            raise ValueError(
                "Ratios must be set for active valves and None for inactive valves"
            )

        total_flow = sum(measurements)

        setpoints = [
            (
                total_flow * ratio if ratio is not None else 0.0
            )  # 0s for inactive to comply with PID typing
            for ratio, active in zip(
                self._ratios, self._flow_balance_controller.get_actives()
            )
        ]
        self._flow_balance_controller.set_setpoints(setpoints)
        self._flow_balance_controller(measurements, time)


class PumpFlowController(_Controller[Ratio, LMin]):
    TUNING = (0.001, 0.001, 0)
    OUTPUT_LIMITS = (0, 1.0)


# class RecoveryFlowControl: #actually this is just for thrusters? will get reused in pvt but not with a single pump. Want to take pump logic out..
#     def __init__(
#         self,
#         mixing_valves: list[Valve],
#         flow_controllers: list[_TemperatureBasedFlowController],
#         flow_balance_controller: FlowBalanceController,
#         pump_controller: PumpFlowController,
#     ):
#         self._mixing_valves = mixing_valves
#         self._flow_controllers = flow_controllers
#         self._flow_balance_controller = flow_balance_controller
#         self._pump_controller = pump_controller

#     def set_actives(self, actives: list[bool]):
#         self._flow_balance_controller.set_actives(actives)

#     def set_temperature_setpoint(self, setpoint: Celsius):
#         for controller in self._flow_controllers:
#             controller.setpoint = setpoint

#     def set_flow_setpoints(self, setpoints: list[LMin]):
#         self._flow_balance_controller.set_setpoints(setpoints)

#     def set_pump_setpoint(self, setpoint: Ratio):
#         self._pump_controller.setpoint = setpoint

#     def get_recovery_flow_setpoints(self, temperature_measurements: list[Celsius], time: datetime):

#         if len(temperature_measurements) != len(self._flow_controllers):
#             raise ValueError("Temperature measurements length must match controllers length")

#         #Set flow setpoints based on temperature measurements
#         flow_setpoints = [
#             controller(measurement, time)
#             for controller, measurement in zip(self._flow_controllers, temperature_measurements)
#         ]


#     def __call__(self, temperature_measurements: list[Celsius], flow_measurements: list[LMin], time: datetime):
#         if len(temperature_measurements) != len(self._flow_controllers):
#             raise ValueError("Temperature measurements length must match controllers length")

#         #Set flow setpoints based on temperature measurements
#         flow_setpoints = [
#             controller(measurement, time)
#             for controller, measurement in zip(self._flow_controllers, temperature_measurements)
#         ]
#         self.set_flow_setpoints(flow_setpoints)
#         self.set_pump_setpoint(sum(flow_setpoints))

#         #Update flow control valves and pump based on flow measurements
#         self._flow_balance_controller(flow_measurements, time)
#         self._pump_controller(sum(flow_measurements), time) #use separate measurement here?
