from datetime import datetime
from typing import cast
from simple_pid import PID

from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import LMin, Ratio


class Controller[ValueUnit: float, SetpointUnit: float]:
    def __init__(
        self,
        initial: ValueUnit,
        setpoint: SetpointUnit,
        tuning: tuple[float, float, float],
        output_limits: tuple[float, float] = (0, 1),
    ):
        kp, ki, kd = tuning or self.TUNING
        self._pid = PID(
            kp,
            ki,
            kd,
            setpoint=setpoint,
            sample_time=None,
            output_limits=output_limits,
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
        return (
            pid_result if pid_result is not None else self._initial
        )  # do we want initial back or None?


class FlowBalanceController:
    def __init__(
        self,
        valves: list[Valve],
        valve_controllers: list[Controller[Ratio, LMin]],
        pump: Pump | None,
        pump_controller: Controller[Ratio, LMin],
    ):
        self._valve_controllers = valve_controllers
        self._pump_controller = pump_controller
        self._valves = valves
        self._pump = pump

    def disable(self):
        for controller in self._valve_controllers:
            if controller.enabled():
                controller.disable()
        self._pump_controller.disable()

    def enable(self, actives: list[bool]):
        self.set_active_valves(actives)
        self._pump_controller.enable()

    @property
    def enabled(self) -> bool:
        return (
            any(controller.enabled() for controller in self._valve_controllers)
            and self._pump_controller.enabled()
        )

    def set_active_valves(self, actives: list[bool]):
        if len(actives) != len(self._valve_controllers):
            raise ValueError("Actives length must match valves length")
        for controller, active in zip(self._valve_controllers, actives):
            if not controller.enabled() and active:
                controller.enable()
            elif controller.enabled() and not active:
                controller.disable()

    def set_pump(self, pump: Pump | None):
        self._pump = pump

    def get_active_valves(self) -> list[bool]:
        return [controller.enabled() for controller in self._valve_controllers]

    def set_setpoint(self, setpoint: LMin):
        for controller in self._valve_controllers:
            controller.setpoint = setpoint

    def set_setpoints(self, setpoints: list[LMin]):
        if len(setpoints) != len(self._valve_controllers):
            raise ValueError("Setpoints length must match valves length")

        for controller, setpoint in zip(self._valve_controllers, setpoints):
            controller.setpoint = setpoint

    def get_setpoints(self) -> list[LMin]:
        return [controller.setpoint for controller in self._valve_controllers]

    def __call__(self, measurements: list[LMin], time: datetime):
        if len(measurements) != len(self._valve_controllers):
            raise ValueError("Measurements length must match valves length")

        if self.enabled:
            controller_values = [
                controller(measurement, time)
                for controller, measurement in zip(
                    self._valve_controllers, measurements
                )
            ]
            offset = 1 - max(*controller_values)
            for value, controller, valve in zip(
                controller_values, self._valve_controllers, self._valves
            ):
                if controller.enabled():
                    valve.setpoint = Stamped(value=value + offset, timestamp=time)
                else:
                    valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=time)
            if self._pump is not None:
                self._pump_controller.setpoint = sum([
                    setpoint * active
                    for setpoint, active in zip(self.get_setpoints(), self.get_active_valves())
                ])
                self._pump.dutypoint = Stamped(
                    value=self._pump_controller(sum(measurements), time), timestamp=time
                )
            else:
                raise ValueError("No active pump")


class FlowDistributionController:
    def __init__(self, valves: list[Valve], tuning):
        self._flow_balance_controller = FlowBalanceController(
            valves,
            tuning,
            close_when_disabled=False,
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
