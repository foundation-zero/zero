from datetime import datetime
from typing import Callable

from transitions import State

from thrs.classes.control import Control, ControlMode
from thrs.classes.machine_state_logger import (
    MachineStateLoggingServiceNoop,
    StateLogger,
)
from thrs.control.controllers import FlowBalanceController, PidController
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pcm, Pump, Valve
from thrs.input_output.definitions.units import Celsius, LMin, Ratio, Tuning
from thrs.input_output.modules.pcm import PcmControlValues, PcmSensorValues
from thrs.orchestration.module import ModuleDescription


class PcmParameters(ThrsValues):
    pcm_discharge_flow: LMin = 5
    pcm_charge_flow: LMin = 5
    minimum_charging_dt: Celsius = 2
    minimum_charging_temperature: Celsius = 60
    pump_tuning: Tuning = (0.01, 0.001, 0)
    supplying_enabled: bool = True
    charging_enabled: bool = True
    module1_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module2_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module3_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module4_flow_balance_tuning: Tuning = (0.05, 0.01, 0)


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> PcmControlValues:
    return PcmControlValues(
        pcm_pump=Pump(
            dutypoint=Stamped(value=0, timestamp=timestamp),
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


class PcmControllerState(ThrsValues):
    pass


class PcmControl(
    Control[
        PcmSensorValues,
        PcmControlValues,
        PcmParameters,
        PcmControlMode,
        PcmControllerState,
    ]
):
    def __init__(
        self,
        parameters: PcmParameters,
        time_fn: Callable[[], datetime],
        state_logger: StateLogger | None = None,
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self.state_logger = state_logger or MachineStateLoggingServiceNoop()
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

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
                ],
                on_exit=[self._deactivate_pump],
            ),
            State(
                name="charging",
                on_enter=[
                    self._set_valves_to_charging,
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
                "conditions": [
                    lambda sensor_values: self._parameters.supplying_enabled,
                    lambda sensor_values: not self._all_discharged(sensor_values),
                ],
            },
            {
                "trigger": "_check_supplying_conditions",
                "source": "supplying",
                "dest": "idle",
                "conditions": lambda sensor_values: not self._parameters.supplying_enabled
                or self._all_discharged(sensor_values),
            },
            {
                "trigger": "_try_charging",
                "source": "idle",
                "dest": "charging",
                "conditions": [
                    lambda sensor_values: self._parameters.charging_enabled,
                    self._heat_available,
                ],
            },
            {
                "trigger": "_check_charging_conditions",
                "source": "charging",
                "dest": "idle",
                "conditions": lambda sensor_values: not self._parameters.charging_enabled
                or not self._sufficient_dt(sensor_values),
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
        return (_INITIAL_CONTROL_VALUES(self._time()), PcmControllerState())

    @StateLogger.log_parameters
    def update_parameters(self, parameters: PcmParameters):
        self._parameters = parameters

    @StateLogger.log_warnings
    def control(
        self, sensor_values: PcmSensorValues
    ) -> tuple[PcmControlValues, PcmControllerState]:
        self._try_supplying(sensor_values) if self.mode.is_idle else None  # type: ignore
        self._try_charging(sensor_values) if self.mode.is_idle else None  # type: ignore

        if self.mode.is_charging:
            self._set_charging_flow_setpoints(sensor_values)
            self._check_charging_conditions(sensor_values)  # type: ignore
        elif self.mode.is_supplying:
            self._set_supplying_flow_setpoints(sensor_values)
            self._check_supplying_conditions(sensor_values)  # type: ignore

        self._control_flow_balance(sensor_values)

        return (self._current_values, PcmControllerState())

    def _all_discharged(self, sensor_values: PcmSensorValues) -> bool:
        return not any(
            (
                sensor_values.pcm_module1.charged.value,
                sensor_values.pcm_module2.charged.value,
                sensor_values.pcm_module3.charged.value,
                sensor_values.pcm_module4.charged.value,
            )
        )

    def _heat_available(self, sensor_values: PcmSensorValues) -> bool:
        return (
            sensor_values.pcm_temperature_producers_return.temperature.value
            > self._parameters.minimum_charging_temperature
        )  # TODO: need to check if flow is available, but the flow meter is in the consumers module

    def _sufficient_dt(self, sensor_values: PcmSensorValues) -> bool:
        return any(
            (
                (
                    sensor_values.pcm_temperature_producers_return.temperature.value
                    - sensor_values.pcm_temperature_module1.temperature.value
                )
                > self._parameters.minimum_charging_dt,
                (
                    sensor_values.pcm_temperature_producers_return.temperature.value
                    - sensor_values.pcm_temperature_module2.temperature.value
                )
                > self._parameters.minimum_charging_dt,
                (
                    sensor_values.pcm_temperature_producers_return.temperature.value
                    - sensor_values.pcm_temperature_module3.temperature.value
                )
                > self._parameters.minimum_charging_dt,
                (
                    sensor_values.pcm_temperature_producers_return.temperature.value
                    - sensor_values.pcm_temperature_module4.temperature.value
                )
                > self._parameters.minimum_charging_dt,
            )
        )

    def _set_supplying_flow_setpoints(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller.set_pump(self._current_values.pcm_pump)
        charged_modules = [
            sensor_values.pcm_module1.charged.value,
            sensor_values.pcm_module2.charged.value,
            sensor_values.pcm_module3.charged.value,
            sensor_values.pcm_module4.charged.value,
        ]

        self._flow_balance_controller.set_active_valves(charged_modules)
        self._flow_balance_controller.set_setpoints(
            [
                self.parameters.pcm_discharge_flow if charged else 0.0
                for charged in charged_modules
            ]
        )

    def _set_charging_flow_setpoints(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller.set_pump(None)

        charging_modules = [
            (
                sensor_values.pcm_temperature_producers_return.temperature.value
                - temp_out
            )
            > self.parameters.minimum_charging_dt
            for temp_out in [
                sensor_values.pcm_temperature_module1.temperature.value,
                sensor_values.pcm_temperature_module2.temperature.value,
                sensor_values.pcm_temperature_module3.temperature.value,
                sensor_values.pcm_temperature_module4.temperature.value,
            ]
        ]

        self._flow_balance_controller.set_active_valves(charging_modules)
        self._flow_balance_controller.set_setpoints(
            [
                self.parameters.pcm_charge_flow if charging else 0.0
                for charging in charging_modules
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
            value=Valve.OPEN, timestamp=self._time()
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
            value=Valve.OPEN,
            timestamp=self._time(),  # Needs to not exceed max flow into pcm's
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
