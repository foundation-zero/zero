from collections.abc import Callable, Sequence
from datetime import datetime
from typing import cast

from simple_pid import PID

from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.controllers import (
    PCM_ANCHOR_DWELL,
    PCM_CHARGED_THRESHOLD,
    PCM_CHARGING_DEADBAND,
    PCM_EXHAUSTED_EFFECTIVENESS,
    PCM_MAX_SAMPLE_GAP,
    PCM_MELT_MARGIN,
    PCM_MELT_TEMP,
    PCM_MIN_FLOW,
    PCM_MODULE_CAPACITY,
    PCM_MODULE_PURGE_VOLUME,
    PCM_STANDBY_LOSS,
    PcmChargeControllerValues,
    PcmChargingState,
    PidControllerValues,
)
from thrs.input_output.definitions.sensor import HeatTransferDevice
from thrs.input_output.definitions.units import (
    DeltaT,
    Joule,
    Liter,
    LMin,
    Ratio,
    Seconds,
    Watt,
)


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
        self._pid_result = None
        self._measurement = None
        self._time = time_fn

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

    def values(self) -> PidControllerValues:
        self._sync_parameters()
        timestamp = self._time()
        return PidControllerValues(
            setpoint=Stamped(value=self.setpoint, timestamp=timestamp),
            measurement=Stamped(value=self._measurement, timestamp=timestamp),
            output=Stamped(value=self._pid_result, timestamp=timestamp),
            error=Stamped(value=self.error, timestamp=timestamp),
            enabled=Stamped(value=self.enabled(), timestamp=timestamp),
            tuning=Stamped(value=self._tuning, timestamp=timestamp),
            components=Stamped(value=self._pid.components, timestamp=timestamp),
        )

    @classmethod
    def zero(cls, timestamp: datetime, setpoint: float = 0.0) -> PidControllerValues:
        return PidControllerValues(
            setpoint=Stamped(value=setpoint, timestamp=timestamp),
            measurement=Stamped(value=None, timestamp=timestamp),
            output=Stamped(value=None, timestamp=timestamp),
            error=Stamped(value=None, timestamp=timestamp),
            enabled=Stamped(value=False, timestamp=timestamp),
            tuning=Stamped(value=(0.0, 0.0, 0.0), timestamp=timestamp),
            components=Stamped(value=(0.0, 0.0, 0.0), timestamp=timestamp),
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
        for controller, active in zip(self._valve_controllers, actives, strict=False):
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

        for controller, setpoint in zip(
            self._valve_controllers, setpoints, strict=False
        ):
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
            for controller, measurement in zip(
                self._valve_controllers, measurements, strict=False
            )
        ]
        offset = 1 - max(*controller_values)
        for value, controller, valve in zip(
            controller_values, self._valve_controllers, self._valves, strict=False
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
                        self.get_setpoints(), self.get_active_valves(), strict=False
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
                    self._ratios,
                    self._flow_balance_controller.get_active_valves(),
                    strict=False,
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
                self._ratios,
                self._flow_balance_controller.get_active_valves(),
                strict=False,
            )
        ]
        self._flow_balance_controller.set_setpoints(setpoints)
        self._flow_balance_controller(measurements)


class PcmChargeController:
    """Estimates the energy stored in one PCM module.

    The energy is integrated from the heat of each circuit through the module, plus
    `heating_power` while `heating` is set, minus PCM_STANDBY_LOSS while nothing flows.
    It is None until the first anchor. A module is anchored full (empty) when, with the
    inlet more than PCM_MELT_MARGIN above (below) PCM_MELT_TEMP,

        |T_out - T_in| / |T_in - PCM_MELT_TEMP| < PCM_EXHAUSTED_EFFECTIVENESS

    holds for PCM_ANCHOR_DWELL. While the PCM melts or freezes it stays at
    PCM_MELT_TEMP, which pulls the outlet towards it and keeps this effectiveness high.
    Once the latent heat is used up, the PCM moves towards the inlet temperature and
    the effectiveness drops to zero. Circuits anchoring in opposite directions cancel.

    The sensors sit in the pipework, so a circuit only counts once its purge volume has
    passed since flow started and all its readings are known. Pass circuits in the order
    of `purge_volumes`.
    """

    def __init__(
        self,
        time_fn: Callable[[], datetime],
        purge_volumes: Sequence[Liter] = (PCM_MODULE_PURGE_VOLUME,),
        capacity: Joule = PCM_MODULE_CAPACITY,
        heating_power: Watt = 0.0,
    ) -> None:
        self._time = time_fn
        self._capacity = capacity
        self._heating_power = heating_power
        self._purge_volumes = tuple(purge_volumes)
        self._purged = [0.0] * len(self._purge_volumes)
        self._energy: Joule | None = None
        self._charging_state = PcmChargingState.IDLE
        self._previous: datetime | None = None
        self._full_since: datetime | None = None
        self._empty_since: datetime | None = None

    def __call__(
        self, *heat_transfer_devices: HeatTransferDevice, heating: bool = False
    ) -> None:
        if len(heat_transfer_devices) != len(self._purge_volumes):
            raise ValueError("Devices length must match purge volumes length")

        timestamp = min(device.heat.timestamp for device in heat_transfer_devices)
        previous, self._previous = self._previous, timestamp
        interval = (timestamp - previous).total_seconds() if previous else 0.0

        self._charging_state = self._state(heat_transfer_devices, heating)

        if not 0 < interval <= PCM_MAX_SAMPLE_GAP:
            self._purged = [0.0] * len(self._purge_volumes)
            return

        settled = [
            self._settle(index, device, interval)
            for index, device in enumerate(heat_transfer_devices)
        ]
        self._integrate(heat_transfer_devices, settled, heating, interval)
        self._anchor(heat_transfer_devices, settled, timestamp)

    def _state(
        self, heat_transfer_devices: Sequence[HeatTransferDevice], heating: bool
    ) -> PcmChargingState:
        heat = sum(
            device.heat.value
            for device in heat_transfer_devices
            if device.heat.value is not None and self._flowing(device)
        ) - (self._heating_power if heating else 0.0)

        if heat < -PCM_CHARGING_DEADBAND:
            return PcmChargingState.CHARGING
        if heat > PCM_CHARGING_DEADBAND:
            return PcmChargingState.DISCHARGING
        return PcmChargingState.IDLE

    def _settle(
        self, index: int, heat_transfer_device: HeatTransferDevice, interval: Seconds
    ) -> bool:
        flow = heat_transfer_device.flow.value
        if (
            flow is None
            or flow < PCM_MIN_FLOW
            or heat_transfer_device.heat.value is None
            or heat_transfer_device.delta_t.value is None
            or heat_transfer_device.temperature_supply.value is None
        ):
            self._purged[index] = 0.0
            return False

        self._purged[index] += flow * interval / 60
        return self._purged[index] >= self._purge_volumes[index]

    def _integrate(
        self,
        heat_transfer_devices: Sequence[HeatTransferDevice],
        settled: Sequence[bool],
        heating: bool,
        interval: Seconds,
    ) -> None:
        if self._energy is None:
            return

        heats = [
            device.heat.value
            for device, ready in zip(heat_transfer_devices, settled, strict=True)
            if ready and device.heat.value is not None
        ]
        if heats:
            power = -sum(heats)
        elif any(
            device.flow.value is None or self._flowing(device)
            for device in heat_transfer_devices
        ):
            power = 0.0
        else:
            power = -PCM_STANDBY_LOSS

        if heating:
            power += self._heating_power

        self._energy = min(max(self._energy + power * interval, 0.0), self._capacity)

    def _anchor(
        self,
        heat_transfer_devices: Sequence[HeatTransferDevice],
        settled: Sequence[bool],
        timestamp: datetime,
    ) -> None:
        drives = [
            self._exhausted_drive(device)
            for device, ready in zip(heat_transfer_devices, settled, strict=True)
            if ready
        ]
        full = any(drive is not None and drive > 0 for drive in drives)
        empty = any(drive is not None and drive < 0 for drive in drives)
        if full and empty:
            full = empty = False

        self._full_since = (self._full_since or timestamp) if full else None
        self._empty_since = (self._empty_since or timestamp) if empty else None

        if self._held(self._full_since, timestamp):
            self._energy = self._capacity
        elif self._held(self._empty_since, timestamp):
            self._energy = 0.0

    @staticmethod
    def _flowing(heat_transfer_device: HeatTransferDevice) -> bool:
        flow = heat_transfer_device.flow.value
        return flow is not None and flow >= PCM_MIN_FLOW

    @staticmethod
    def _exhausted_drive(heat_transfer_device: HeatTransferDevice) -> DeltaT | None:
        """T_in - PCM_MELT_TEMP if the circuit shows no phase change left, else None."""
        inlet = heat_transfer_device.temperature_supply.value
        delta_t = heat_transfer_device.delta_t.value
        if inlet is None or delta_t is None:
            return None

        drive = inlet - PCM_MELT_TEMP
        if abs(drive) <= PCM_MELT_MARGIN:
            return None
        if abs(delta_t) >= PCM_EXHAUSTED_EFFECTIVENESS * abs(drive):
            return None
        return drive

    @staticmethod
    def _held(since: datetime | None, timestamp: datetime) -> bool:
        return (
            since is not None
            and (timestamp - since).total_seconds() >= PCM_ANCHOR_DWELL
        )

    @property
    def charge(self) -> Ratio | None:
        return None if self._energy is None else self._energy / self._capacity

    @property
    def charged(self) -> bool | None:
        return None if self.charge is None else self.charge > PCM_CHARGED_THRESHOLD

    def values(self) -> PcmChargeControllerValues:
        timestamp = self._time()
        return PcmChargeControllerValues(
            charge=Stamped(value=self.charge, timestamp=timestamp),
            energy=Stamped(value=self._energy, timestamp=timestamp),
            charged=Stamped(value=self.charged, timestamp=timestamp),
            charging_state=Stamped(value=self._charging_state, timestamp=timestamp),
        )
