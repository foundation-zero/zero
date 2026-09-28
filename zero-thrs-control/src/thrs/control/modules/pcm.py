from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Annotated

from pydantic import Field, model_validator
from transitions import State

from thrs.classes.control import Control, ControlMode
from thrs.classes.machine_state_logger import StateLogger
from thrs.control.controllers import (
    FlowBalanceController,
    PcmChargeController,
    PidController,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pcm, Pump, Valve
from thrs.input_output.definitions.controllers import (
    PCM_HEATING_ELEMENT_POWER,
    PCM_MODULE1_FRESHWATER_PURGE_VOLUME,
    PCM_MODULE1_PURGE_VOLUME,
    PcmChargeControllerValues,
    PcmChargeStatus,
    PcmChargingState,
)
from thrs.input_output.definitions.units import (
    Celsius,
    LMin,
    Ratio,
    Seconds,
    Tuning,
)
from thrs.input_output.modules.pcm import PcmControlValues, PcmSensorValues
from thrs.orchestration.module import ModuleDescription


class PcmParameters(ThrsValues):
    pcm_discharge_flow: LMin = 5
    pcm_charge_flow: LMin = 5
    minimum_charging_temperature: Annotated[
        Celsius,
        Field(description="Range for thermal charging", ge=65, le=80),
    ] = 65
    pump_tuning: Tuning = (0.01, 0.001, 0)
    charging_requested: Annotated[
        bool,
        Field(description="Keep trying to charge the PCM modules while possible"),
    ] = False
    supplying_requested: Annotated[
        bool,
        Field(
            description="Keep trying to supply heat from the PCM modules while possible"
        ),
    ] = False
    grace_period: Annotated[
        Seconds,
        Field(
            description="Grace period after entering charging/supplying before the stall guard checks a module's charging_state",
            ge=0,
        ),
    ] = 120
    stall_duration: Annotated[
        Seconds,
        Field(
            description="How long a module's charging_state may fail to show it actually (dis)charging before it is dropped as stalled",
            ge=0,
        ),
    ] = 120
    retry_delay: Annotated[
        Seconds,
        Field(
            description="Lockout before retrying a mode after all its modules stalled and were dropped",
            ge=0,
        ),
    ] = 600
    module1_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module2_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module3_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module4_flow_balance_tuning: Tuning = (0.05, 0.01, 0)

    @model_validator(mode="after")
    def check_not_both_requested(self):
        if self.charging_requested and self.supplying_requested:
            raise ValueError("Charging and supplying cannot both be requested")
        return self

    @model_validator(mode="after")
    def check_charging_can_anchor_full(self):
        bound = PcmChargeController.minimum_charging_temperature(self.pcm_charge_flow)
        if self.minimum_charging_temperature <= bound:
            raise ValueError(
                f"Minimum charging temperature must be above {bound:.1f} C at a "
                f"charge flow of {self.pcm_charge_flow} l/min"
            )
        return self


class PcmControllerState(ThrsValues):
    module1_charge_controller: PcmChargeControllerValues
    module2_charge_controller: PcmChargeControllerValues
    module3_charge_controller: PcmChargeControllerValues
    module4_charge_controller: PcmChargeControllerValues


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> PcmControlValues:  # noqa: N802
    return PcmControlValues(
        pcm_pump=Pump(
            dutypoint=Stamped(value=0.1, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        pcm_switch_charging_return=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        pcm_flowcontrol_module1=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        pcm_flowcontrol_module2=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        pcm_flowcontrol_module3=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        pcm_flowcontrol_module4=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        pcm_switch_discharging=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        pcm_switch_charging_supply=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        pcm_switch_consumers=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        pcm_module1=Pcm(on=Stamped(value=False, timestamp=timestamp)),
    )


def _INITIAL_CHARGE_CONTROLLER_VALUES(  # noqa: N802
    timestamp: datetime,
) -> PcmChargeControllerValues:
    return PcmChargeControllerValues(
        charge=Stamped(value=None, timestamp=timestamp),
        energy=Stamped(value=None, timestamp=timestamp),
        charge_status=Stamped(value=PcmChargeStatus.UNKNOWN, timestamp=timestamp),
        charging_state=Stamped(value=PcmChargingState.IDLE, timestamp=timestamp),
    )


def _INITIAL_CONTROLLER_STATE(timestamp: datetime) -> PcmControllerState:  # noqa: N802
    return PcmControllerState(
        module1_charge_controller=_INITIAL_CHARGE_CONTROLLER_VALUES(timestamp),
        module2_charge_controller=_INITIAL_CHARGE_CONTROLLER_VALUES(timestamp),
        module3_charge_controller=_INITIAL_CHARGE_CONTROLLER_VALUES(timestamp),
        module4_charge_controller=_INITIAL_CHARGE_CONTROLLER_VALUES(timestamp),
    )


class PcmControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"

    @property
    def is_supplying(self) -> bool:
        return self.mode == "supplying"

    @property
    def is_charging(self) -> bool:
        return self.mode == "charging"

    @property
    def is_boosting(self) -> bool:
        return self.mode == "boosting"


class PcmControl(
    Control[
        PcmSensorValues,
        PcmControlValues,
        PcmParameters,
        PcmControlMode,
        PcmControllerState,
    ]
):
    state: str  # Value set by Machine transitions logic

    def __init__(
        self,
        parameters: PcmParameters,
        time_fn: Callable[[], datetime],
        state_logger: StateLogger,
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self.state_logger = state_logger
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )
        self._mode_entered_at: datetime | None = None
        self._module_last_active: dict[PcmChargeController, datetime] = {}
        self._dropped_modules: set[PcmChargeController] = set()
        self._charging_retry_until: datetime | None = None
        self._supplying_retry_until: datetime | None = None

        self._init_state_machine_states()
        self._init_state_machine_transitions()
        self._state_machine = self.state_logger.create_logged_state_machine(
            self,
            transitions=self._transitions,
            states=self._states,
            initial="idle",
        )
        self._init_controllers()
        self.state_logger.log_parameters_initial_state(parameters)

    def _init_state_machine_states(self):
        self._states = [
            State(
                name="supplying",
                on_enter=[
                    self._set_valves_to_supplying,
                    self._activate_pump,
                    self._start_mode_tracking,
                ],
                on_exit=[self._deactivate_pump],
            ),
            State(
                name="charging",
                on_enter=[
                    self._set_valves_to_charging,
                    self._start_mode_tracking,
                ],
            ),
            State(
                name="boosting",
                on_enter=[
                    self._set_valves_to_boosting,
                ],
            ),
            State(
                name="idle",
                on_enter=[self._set_valves_to_idle, self._disable_flow_balancing],
                on_exit=self._enable_flow_balancing,
            ),
        ]

    def _init_state_machine_transitions(self):
        self._transitions = [
            {
                "trigger": "_try_supplying",
                "source": "idle",
                "dest": "supplying",
                "conditions": self._supplying_available,
            },
            {
                "trigger": "_check_supplying_conditions",
                "source": "supplying",
                "dest": "idle",
                "conditions": self._supplying_should_stop,
            },
            {
                "trigger": "_try_charging",
                "source": "idle",
                "dest": "charging",
                "conditions": self._charging_available,
            },
            {
                "trigger": "_check_charging_conditions",
                "source": "charging",
                "dest": "idle",
                "conditions": self._charging_should_stop,
            },
        ]

    def _init_controllers(self):
        if not hasattr(self, "_state_machine") or self._state_machine is None:
            raise ValueError(
                "State machine must be initialized before creating control methods"
            )

        self._pump_flow_controller = PidController[Ratio, LMin](
            self._current_values.pcm_pump.dutypoint.value,
            0,
            lambda: self._parameters.pump_tuning,
            self._time,
            output_limits=(0.1, 1),
        )

        self.module1_flow_controller = PidController[Ratio, LMin](
            self._current_values.pcm_flowcontrol_module1.setpoint.value,
            0,
            lambda: self._parameters.module1_flow_balance_tuning,
            self._time,
        )

        self.module2_flow_controller = PidController[Ratio, LMin](
            self._current_values.pcm_flowcontrol_module2.setpoint.value,
            0,
            lambda: self._parameters.module2_flow_balance_tuning,
            self._time,
        )

        self.module3_flow_controller = PidController[Ratio, LMin](
            self._current_values.pcm_flowcontrol_module3.setpoint.value,
            0,
            lambda: self._parameters.module3_flow_balance_tuning,
            self._time,
        )

        self.module4_flow_controller = PidController[Ratio, LMin](
            self._current_values.pcm_flowcontrol_module4.setpoint.value,
            0,
            lambda: self._parameters.module4_flow_balance_tuning,
            self._time,
        )

        self._flow_balance_controller = FlowBalanceController(
            [
                self._current_values.pcm_flowcontrol_module1,
                self._current_values.pcm_flowcontrol_module2,
                self._current_values.pcm_flowcontrol_module3,
                self._current_values.pcm_flowcontrol_module4,
            ],
            [
                self.module1_flow_controller,
                self.module2_flow_controller,
                self.module3_flow_controller,
                self.module4_flow_controller,
            ],
            self._current_values.pcm_pump,
            self._pump_flow_controller,
            self._time,
        )

        self.module1_charge_controller = PcmChargeController(
            self._time,
            (PCM_MODULE1_PURGE_VOLUME, PCM_MODULE1_FRESHWATER_PURGE_VOLUME),
            heating_power=PCM_HEATING_ELEMENT_POWER,
        )
        self.module2_charge_controller = PcmChargeController(self._time)
        self.module3_charge_controller = PcmChargeController(self._time)
        self.module4_charge_controller = PcmChargeController(self._time)

    @property
    def parameters(self) -> PcmParameters:
        return self._parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> PcmControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return PcmControlMode(mode=initial_mode)

    @property
    def mode(self) -> PcmControlMode:
        mode: str = self.state  # type: ignore
        return PcmControlMode(mode=mode)

    def initial(self) -> tuple[PcmControlValues, PcmControllerState]:
        return (
            _INITIAL_CONTROL_VALUES(self._time()),
            _INITIAL_CONTROLLER_STATE(self._time()),
        )

    def reset(self) -> None:
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )
        self._mode_entered_at = None
        self._module_last_active = {}
        self._dropped_modules = set()
        self._charging_retry_until = None
        self._supplying_retry_until = None
        self._state_machine.set_state(self._state_machine.initial)  # type: ignore
        self._init_controllers()

    @StateLogger.log_parameters
    def update_parameters(self, parameters: PcmParameters):
        self._parameters = parameters

    def update_controls(self, control_values: PcmControlValues):
        self._current_values.update_in_place(control_values)

    @StateLogger.log_warnings
    def control(
        self, sensor_values: PcmSensorValues
    ) -> tuple[PcmControlValues, PcmControllerState]:
        self._try_supplying(sensor_values) if self.mode.is_idle else None  # type: ignore
        self._try_charging(sensor_values) if self.mode.is_idle else None  # type: ignore

        if self.mode.is_charging:
            self._update_dropped_modules(
                PcmChargingState.CHARGING, PcmChargeStatus.FULL
            )
            self._set_charging_flow_setpoints(sensor_values)
            self._check_charging_conditions(sensor_values)  # type: ignore
        elif self.mode.is_supplying:
            self._update_dropped_modules(
                PcmChargingState.DISCHARGING, PcmChargeStatus.EMPTY
            )
            self._set_supplying_flow_setpoints(sensor_values)
            self._check_supplying_conditions(sensor_values)  # type: ignore

        controller_state = self._update_controllers(sensor_values)

        return (self._current_values, controller_state)

    def _update_controllers(self, sensor_values: PcmSensorValues) -> PcmControllerState:
        self._control_flow_balance(sensor_values)

        self.module1_charge_controller(
            sensor_values.pcm_heat_module1,
            sensor_values.pcm_heat_module1_freshwater,
            heating=self._current_values.pcm_module1.on.value,
        )
        self.module2_charge_controller(sensor_values.pcm_heat_module2)
        self.module3_charge_controller(sensor_values.pcm_heat_module3)
        self.module4_charge_controller(sensor_values.pcm_heat_module4)

        return PcmControllerState(
            module1_charge_controller=self.module1_charge_controller.values(),
            module2_charge_controller=self.module2_charge_controller.values(),
            module3_charge_controller=self.module3_charge_controller.values(),
            module4_charge_controller=self.module4_charge_controller.values(),
        )

    def _modules(self) -> list[PcmChargeController]:
        return [
            self.module1_charge_controller,
            self.module2_charge_controller,
            self.module3_charge_controller,
            self.module4_charge_controller,
        ]

    def _eligible(
        self, module: PcmChargeController, exhausted: PcmChargeStatus
    ) -> bool:
        return module.charge_status is not exhausted

    def _active(self, module: PcmChargeController, exhausted: PcmChargeStatus) -> bool:
        """Eligible and not dropped as stalled this cycle."""
        return self._eligible(module, exhausted) and module not in self._dropped_modules

    def _valves_settled(
        self, sensor_values: PcmSensorValues, tolerance: Ratio = 0.05
    ) -> bool:
        pairs = [
            (
                self._current_values.pcm_switch_charging_return,
                sensor_values.pcm_switch_charging_return,
            ),
            (
                self._current_values.pcm_switch_discharging,
                sensor_values.pcm_switch_discharging,
            ),
            (
                self._current_values.pcm_switch_charging_supply,
                sensor_values.pcm_switch_charging_supply,
            ),
            (
                self._current_values.pcm_switch_consumers,
                sensor_values.pcm_switch_consumers,
            ),
        ]
        return all(
            abs(sensor_valve.position_rel.value - control_valve.setpoint.value)
            <= tolerance
            for control_valve, sensor_valve in pairs
        )

    def _locked_out(self, until: datetime | None) -> bool:
        return until is not None and self._time() < until

    def _charging_available(self, sensor_values: PcmSensorValues) -> bool:
        return (
            self._parameters.charging_requested
            and self._valves_settled(sensor_values)
            and sensor_values.pcm_temperature_producers_return.temperature.value
            > self._parameters.minimum_charging_temperature
            and any(
                self._eligible(module, PcmChargeStatus.FULL)
                for module in self._modules()
            )
            and not self._locked_out(self._charging_retry_until)
        )

    def _supplying_available(self, sensor_values: PcmSensorValues) -> bool:
        return (
            self._parameters.supplying_requested
            and self._valves_settled(sensor_values)
            and any(
                self._eligible(module, PcmChargeStatus.EMPTY)
                for module in self._modules()
            )
            and not self._locked_out(self._supplying_retry_until)
        )

    def _charging_should_stop(self, sensor_values: PcmSensorValues) -> bool:
        if not any(
            self._active(module, PcmChargeStatus.FULL) for module in self._modules()
        ):
            if self._dropped_modules:
                self._charging_retry_until = self._time() + timedelta(
                    seconds=self._parameters.retry_delay
                )
            return True
        return not self._parameters.charging_requested

    def _supplying_should_stop(self, sensor_values: PcmSensorValues) -> bool:
        if not any(
            self._active(module, PcmChargeStatus.EMPTY) for module in self._modules()
        ):
            if self._dropped_modules:
                self._supplying_retry_until = self._time() + timedelta(
                    seconds=self._parameters.retry_delay
                )
            return True
        return not self._parameters.supplying_requested

    def _start_mode_tracking(self, sensor_values: PcmSensorValues):
        entered_at = self._time()
        self._mode_entered_at = entered_at
        grace_end = entered_at + timedelta(seconds=self._parameters.grace_period)
        self._module_last_active = dict.fromkeys(self._modules(), grace_end)
        self._dropped_modules = set()

    def _update_dropped_modules(
        self, expected_state: PcmChargingState, exhausted: PcmChargeStatus
    ) -> None:
        if self._mode_entered_at is None:
            return
        grace_elapsed = (
            self._time() - self._mode_entered_at
        ).total_seconds() >= self._parameters.grace_period

        # Exhausted modules get no flow, so they never (dis)charge; don't drop them.
        for module in self._modules():
            if not self._active(module, exhausted):
                continue
            if module.charging_state is expected_state:
                self._module_last_active[module] = self._time()
            elif (
                grace_elapsed
                and (self._time() - self._module_last_active[module]).total_seconds()
                >= self._parameters.stall_duration
            ):
                self._dropped_modules.add(module)

    def _set_supplying_flow_setpoints(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller.set_pump(self._current_values.pcm_pump)
        actives = [
            self._active(module, PcmChargeStatus.EMPTY) for module in self._modules()
        ]

        self._flow_balance_controller.set_active_valves(actives)
        self._flow_balance_controller.set_setpoints(
            [
                self.parameters.pcm_discharge_flow if is_active else 0.0
                for is_active in actives
            ]
        )

    def _set_charging_flow_setpoints(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller.set_pump(None)
        actives = [
            self._active(module, PcmChargeStatus.FULL) for module in self._modules()
        ]

        self._flow_balance_controller.set_active_valves(actives)
        self._flow_balance_controller.set_setpoints(
            [
                self.parameters.pcm_charge_flow if is_active else 0.0
                for is_active in actives
            ]
        )

    def _disable_flow_balancing(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller.disable()

    def _enable_flow_balancing(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller.enable([True, True, True, True])

    def _control_flow_balance(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller(
            [
                sensor_values.pcm_flow_module1.flow.value,
                sensor_values.pcm_flow_module2.flow.value,
                sensor_values.pcm_flow_module3.flow.value,
                sensor_values.pcm_flow_module4.flow.value,
            ]
        )

    def _set_valves_to_idle(self, sensor_values: PcmSensorValues):
        self._current_values.pcm_switch_charging_return.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.pcm_switch_discharging.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.pcm_switch_charging_supply.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.pcm_switch_consumers.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

    def _set_valves_to_supplying(self, sensor_values: PcmSensorValues):
        self._current_values.pcm_switch_charging_return.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.pcm_switch_discharging.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_values.pcm_switch_charging_supply.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.pcm_switch_consumers.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

    def _set_valves_to_charging(self, sensor_values: PcmSensorValues):
        self._current_values.pcm_switch_charging_return.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_values.pcm_switch_discharging.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.pcm_switch_charging_supply.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_values.pcm_switch_consumers.setpoint = Stamped(
            value=Valve.CLOSED,
            timestamp=self._time(),
        )

    def _set_valves_to_boosting(self, sensor_values: PcmSensorValues):
        self._current_values.pcm_switch_charging_return.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )
        self._current_values.pcm_switch_discharging.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_values.pcm_switch_charging_supply.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )
        self._current_values.pcm_switch_consumers.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time()
        )

    def _activate_pump(self, sensor_values: PcmSensorValues):
        self._current_values.pcm_pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: PcmSensorValues):
        self._current_values.pcm_pump.on = Stamped(value=False, timestamp=self._time())


class PcmAlarms(BaseAlarms):
    pass


PCM_MODULE_DESCRIPTION = ModuleDescription(
    PcmSensorValues,
    PcmControlValues,
    PcmParameters,
    PcmControl,
    PcmControlMode,
    PcmControllerState,
    PcmAlarms,
)
