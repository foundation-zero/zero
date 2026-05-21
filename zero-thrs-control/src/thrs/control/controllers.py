from datetime import datetime
from typing import Callable, cast
from simple_pid import PID

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import LMin, Ratio


class PidController[ActuatorUnit: float, MeasurementUnit: float]:
    def __init__(
        self,
        initial: ActuatorUnit,
        setpoint: MeasurementUnit | Callable[[], MeasurementUnit],
        tuning: tuple[float, float, float] | Callable[[], tuple[float, float, float]],
        time_fn: Callable[[], datetime],
        output_limits: tuple[float, float] | Callable[[], tuple[float, float]] = (0, 1),
    ):
        self._setpoint_getter = setpoint if callable(setpoint) else None
        self._tuning_getter = tuning if callable(tuning) else None
        self._output_limits_getter = output_limits if callable(output_limits) else None

        self._setpoint = setpoint() if callable(setpoint) else setpoint
        self._tuning = tuning() if callable(tuning) else tuning
        self._output_limits = (
            output_limits() if callable(output_limits) else output_limits
        )

        kp, ki, kd = self._tuning

        initial_setpoint = self._setpoint
        self._pid = PID(
            kp,
            ki,
            kd,
            setpoint=initial_setpoint,
            sample_time=None,
            output_limits=self._output_limits,
            auto_mode=False,
            time_fn=lambda: time_fn().timestamp(),
        )
        self._initial = initial

    def _sync_parameters(self):
        if self._tuning_getter:
            self._tuning = self._tuning_getter()
            self._pid.tunings = self._tuning

        if self._setpoint_getter:
            self._setpoint = self._setpoint_getter()
            self._pid.setpoint = self._setpoint

        if self._output_limits_getter:
            self._output_limits = self._output_limits_getter()
            self._pid.output_limits = self._output_limits

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
    def setpoint(self) -> MeasurementUnit:
        return cast(MeasurementUnit, self._pid.setpoint)

    @setpoint.setter
    def setpoint(self, value: MeasurementUnit):
        self._pid.setpoint = value

    def __call__(self, measurement: MeasurementUnit | None) -> ActuatorUnit:
        self._sync_parameters()
        self._measurement = measurement

        if measurement is None:
            self._pid_result = None
        else:
            self._pid_result = cast(ActuatorUnit | None, self._pid(measurement))
        return (
            self._pid_result if self._pid_result is not None else self._initial
        )  # TODO: is returning self._initial desireable? Perhaps better return either None or last value. Better handled in the control than in here..

    @property
    def error(self) -> MeasurementUnit | None:
        return cast(MeasurementUnit | None, self._pid._last_error)  # type: ignore

    def values(
        self, sensor_values: ThrsValues, parameters: ThrsValues, time: datetime
    ) -> PidControllerValues:
        return PidControllerValues(
            setpoint=Stamped(value=self.setpoint, timestamp=time),
            measurement=Stamped(value=self._measurement, timestamp=time),
            output=Stamped(value=self._pid_result, timestamp=time),
            error=Stamped(value=self.error, timestamp=time),
            enabled=Stamped(value=self.enabled(), timestamp=time),
            tuning=Stamped(value=self._tuning, timestamp=time),
            components=Stamped(value=self._pid.components, timestamp=time),
        )


class FlowBalanceController:
    def __init__(
        self,
        valves: list[Valve],
        valve_controllers: list[PidController[Ratio, LMin]],
        pump: Pump | None = None,
        pump_controller: PidController[Ratio, LMin] | None = None,
        time_fn: Callable[[], datetime] = datetime.now,
    ):
        self._valve_controllers = valve_controllers
        self._pump_controller = pump_controller
        self._valves = valves
        self._pump = pump
        self._time = time_fn

    def disable(self):
        for controller in self._valve_controllers:
            if controller.enabled():
                controller.disable()
        if self._pump_controller is not None:
            self._pump_controller.disable()

    def enable(self, actives: list[bool]):
        self.set_active_valves(actives)
        if self._pump_controller is not None:
            self._pump_controller.enable()

    @property
    def enabled(self) -> bool:
        return any(controller.enabled() for controller in self._valve_controllers) or (
            self._pump_controller is not None and self._pump_controller.enabled()
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

    def __call__(self, measurements: list[LMin]):
        if not self.enabled:
            return

        if len(measurements) != len(self._valve_controllers):
            raise ValueError("Measurements length must match valves length")
        controller_values = [
            controller(measurement)
            for controller, measurement in zip(self._valve_controllers, measurements)
        ]
        offset = 1 - max(*controller_values)
        for value, controller, valve in zip(
            controller_values, self._valve_controllers, self._valves
        ):
            if controller.enabled():
                valve.setpoint = Stamped(value=value + offset, timestamp=self._time())
            else:
                valve.setpoint = Stamped(value=Valve.CLOSED, timestamp=self._time())
        if self._pump is not None and self._pump_controller is not None:
            self._pump_controller.setpoint = sum(
                [
                    setpoint * active
                    for setpoint, active in zip(
                        self.get_setpoints(), self.get_active_valves()
                    )
                ]
            )
            self._pump.dutypoint = Stamped(
                value=self._pump_controller(sum(measurements)),
                timestamp=self._time(),
            )


class FlowDistributionController:
    def __init__(
        self,
        valves: list[Valve],
        valve_controllers: list[PidController[Ratio, LMin]],
    ):
        self._flow_balance_controller = FlowBalanceController(valves, valve_controllers)

    def set_active_valves(self, actives: list[bool]):
        self._flow_balance_controller.set_active_valves(actives)

    def set_ratios(self, ratios: list[Ratio | None]):
        if len(ratios) != (len(self._flow_balance_controller._valve_controllers)):
            raise ValueError("Ratios length must be valves length")
        if sum(ratio for ratio in ratios if ratio is not None) != 1.0:
            raise ValueError("Ratios must sum to 1.0")

        self._ratios = ratios

    def __call__(self, measurements: list[LMin]):
        if len(measurements) != len(self._flow_balance_controller._valve_controllers):
            raise ValueError("Measurements length must match valves length")
        if any(
            (
                True
                for ratio, active in zip(
                    self._ratios, self._flow_balance_controller.get_active_valves()
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
                self._ratios, self._flow_balance_controller.get_active_valves()
            )
        ]
        self._flow_balance_controller.set_setpoints(setpoints)
        self._flow_balance_controller(measurements)
