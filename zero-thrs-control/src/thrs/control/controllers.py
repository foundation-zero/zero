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
    PCM_EXHAUSTED_DT,
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
    """Estimates the stored energy of one PCM module from its own heat balance.

    Inside the melting plateau the module sits at ~58 C whatever the phase fraction, so
    temperature says nothing about how far the phase front has travelled and only
    integrated heat does. At the ends of the plateau it is the other way round: the
    integral has drifted, and temperature says exactly where we are. So the energy is
    integrated continuously and re-anchored to empty or full whenever a module's outlet
    converges on its inlet while the inlet is clearly past the melting point. That
    convergence, not any absolute outlet temperature, is what says the phase change has
    run out: the manufacturer quotes a 50-55 C outlet throughout a normal discharge,
    which reflects the exchanger approach rather than the state of charge.

    A module can have more than one circuit through it (module 1 is charged by the thrs
    loop and discharged by the freshwater system), so every circuit is passed on each
    call, in the order its purge volume was given. Module 1 also has an electric element,
    whose heat goes straight into the cell and so never appears in any circuit: give its
    rating as `heating_power` and say on each call whether it is switched on, or the
    estimate will drift by however long it runs.
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
        # A longer gap means we stopped seeing the module, not that nothing happened.
        usable = 0 < interval <= PCM_MAX_SAMPLE_GAP

        self._charging_state = self._state(heat_transfer_devices, heating)
        settled = [
            self._settle(index, device, interval if usable else 0.0)
            for index, device in enumerate(heat_transfer_devices)
        ]

        if not usable:
            return

        self._integrate(heat_transfer_devices, settled, heating, interval)
        self._anchor(heat_transfer_devices, settled, timestamp)

    def _state(
        self, heat_transfer_devices: Sequence[HeatTransferDevice], heating: bool
    ) -> PcmChargingState:
        flowing = [
            device
            for device in heat_transfer_devices
            if device.flow.value >= PCM_MIN_FLOW
        ]
        # A module taking heat from its element is charging even with nothing flowing.
        heat = sum(device.heat.value for device in flowing) - (
            self._heating_power if heating else 0.0
        )

        if heat < -PCM_CHARGING_DEADBAND:
            return PcmChargingState.CHARGING
        if heat > PCM_CHARGING_DEADBAND:
            return PcmChargingState.DISCHARGING
        return PcmChargingState.IDLE

    def _settle(
        self, index: int, heat_transfer_device: HeatTransferDevice, interval: Seconds
    ) -> bool:
        """Whether this circuit has been flushed since flow started.

        The temperature sensors sit in the pipework, so without flow they read whatever
        was last pushed past them. Counting litres rather than seconds makes the wait
        scale with the flow that is actually clearing them.
        """
        if heat_transfer_device.flow.value < PCM_MIN_FLOW:
            self._purged[index] = 0.0
            return False

        self._purged[index] += heat_transfer_device.flow.value * interval / 60
        return self._purged[index] >= self._purge_volumes[index]

    def _integrate(
        self,
        heat_transfer_devices: Sequence[HeatTransferDevice],
        settled: Sequence[bool],
        heating: bool,
        interval: Seconds,
    ) -> None:
        if self._energy is None:
            return  # No reference to integrate onto until an end point has been seen.

        if any(settled):
            power = -sum(  # Negative heat flows into the module.
                device.heat.value
                for device, ready in zip(heat_transfer_devices, settled, strict=True)
                if ready
            )
        elif any(device.flow.value >= PCM_MIN_FLOW for device in heat_transfer_devices):
            power = 0.0  # Flowing but still flushing: the readings mean nothing yet.
        else:
            power = -PCM_STANDBY_LOSS

        if heating:
            # Straight into the cell, so it counts whether or not anything is flowing.
            power += self._heating_power

        self._energy = min(max(self._energy + power * interval, 0.0), self._capacity)

    def _anchor(
        self,
        heat_transfer_devices: Sequence[HeatTransferDevice],
        settled: Sequence[bool],
        timestamp: datetime,
    ) -> None:
        exhausted = [
            device
            for device, ready in zip(heat_transfer_devices, settled, strict=True)
            if ready
            and device.temperature_supply.value is not None
            and abs(device.delta_t.value) < PCM_EXHAUSTED_DT
        ]
        full = any(
            device.temperature_supply.value > PCM_MELT_TEMP + PCM_MELT_MARGIN
            for device in exhausted
            if device.temperature_supply.value is not None
        )
        empty = any(
            device.temperature_supply.value < PCM_MELT_TEMP - PCM_MELT_MARGIN
            for device in exhausted
            if device.temperature_supply.value is not None
        )
        if full and empty:
            full = empty = False  # Circuits disagree, so neither is evidence.

        self._full_since = (self._full_since or timestamp) if full else None
        self._empty_since = (self._empty_since or timestamp) if empty else None

        if self._held(self._full_since, timestamp):
            self._energy = self._capacity
        elif self._held(self._empty_since, timestamp):
            self._energy = 0.0

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
    def charged(self) -> bool:
        """An uncalibrated module counts as available.

        Modules are selected for discharge on this flag, and discharging is what makes
        the empty anchor fire, so treating unknown as not charged would leave a module
        that never gets discharged and therefore never becomes known.
        """
        return self.charge is None or self.charge > PCM_CHARGED_THRESHOLD

    def values(self) -> PcmChargeControllerValues:
        timestamp = self._time()
        return PcmChargeControllerValues(
            charge=Stamped(value=self.charge, timestamp=timestamp),
            energy=Stamped(value=self._energy, timestamp=timestamp),
            charged=Stamped(value=self.charged, timestamp=timestamp),
            charging_state=Stamped(value=self._charging_state, timestamp=timestamp),
        )
