from collections.abc import Callable
from datetime import datetime
from typing import Annotated

from pydantic import model_validator
from statemachine import State, StateChart

from thrs.classes.control import Control
from thrs.control.controllers import PidController
from thrs.control.modules.pvt.io import IDLE_MIX_POSITION
from thrs.control.state import ControlMode
from thrs.input_output.base import Stamped, ThrsValues, component_meta
from thrs.input_output.definitions import control, sensor
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import Celsius, Ratio, Tuning

RECOVERY_MIX_UPPER_BOUND: Ratio = 0.2
RECOVERY_MIX_LOWER_BOUND: Ratio = 0.05


class PvtGroupSensorValues(ThrsValues):
    pump: sensor.Pump
    temperature_supply: sensor.TemperatureSensor
    temperature_return: sensor.TemperatureSensor
    pressure: sensor.PressureSensor
    mix: sensor.Valve
    max_temperature_strings: sensor.CalculatedTemperature


class PvtGroupControlValues(ThrsValues):
    pump: control.Pump
    mix: control.Valve


class PvtGroupParameters(ThrsValues):
    warmup_temperature: Celsius
    recovery_temperature: Celsius
    warmup_mix_tuning: Tuning
    pump_tuning: Tuning
    minimum_pump_dutypoint: Ratio
    recovery_activation_string_temperature: Celsius
    minimum_return_temperature: Celsius

    @model_validator(mode="after")
    def check_temperature_setpoints(self):
        if self.recovery_temperature < self.warmup_temperature:
            raise ValueError(
                "Recovery temperature must be greater than warmup temperature"
            )
        if self.warmup_temperature < self.minimum_return_temperature:
            raise ValueError(
                "Warmup temperature must be greater than minimum return temperature"
            )
        return self


class PvtGroupControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"


class PvtGroupControllerState(ControlMode):
    pvt_group_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pvt_group_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]


class _PvtGroupStateMachine(StateChart["PvtGroupControl"]):
    """Each event takes the first of its transitions whose condition holds."""

    # An error in a guard or action raises instead of becoming an unhandled event.
    catch_errors_as_events = False

    idle = State(
        initial=True,
        enter=["_set_mix_to_idle_position", "_disable_warmup_mix", "_deactivate_pump"],
        exit=["_enable_warmup_mix", "_activate_pump"],
    )
    warmup = State(enter="_set_pump_to_minimum_dutypoint")
    recovery = State(enter="_enable_pump_control", exit="_disable_pump_control")

    check_temperatures = warmup.from_(idle, cond="_string_warm") | idle.from_(
        warmup, recovery, cond="_low_return_temperature"
    )
    check_mix = recovery.from_(warmup, cond="_mix_open") | warmup.from_(
        recovery, cond="_mix_closed"
    )


class PvtGroupControl(
    Control[
        PvtGroupSensorValues,
        PvtGroupControlValues,
        PvtGroupParameters,
        PvtGroupControlMode,
        PvtGroupControllerState,
    ]
):
    def __init__(
        self,
        parameters: PvtGroupParameters,
        time_fn: Callable[[], datetime],
        initial_control_values: PvtGroupControlValues,
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = initial_control_values

        # Starting with a mode set skips idle's enter actions: the first outputs are
        # the initial control values.
        self._state: str = _PvtGroupStateMachine.idle.value
        self._state_machine = _PvtGroupStateMachine(model=self, state_field="_state")
        self._init_controllers()

    def _init_controllers(self):
        self._warmup_mix_controller = PidController[Ratio, Celsius](
            self._current_values.mix.setpoint.value,
            lambda: self._parameters.warmup_temperature,
            lambda: self._parameters.warmup_mix_tuning,
            self._time,
        )

        self._pump_controller = PidController[Ratio, Celsius](
            self._current_values.pump.dutypoint.value,
            lambda: self._parameters.recovery_temperature,
            lambda: self._parameters.pump_tuning,
            self._time,
            lambda: (self._parameters.minimum_pump_dutypoint, 1),
        )

    @property
    def parameters(self) -> PvtGroupParameters:
        return self._parameters

    @property
    def mode(self) -> PvtGroupControlMode:
        return PvtGroupControlMode(mode=self._state)

    def update_parameters(self, parameters: PvtGroupParameters):
        self._parameters = parameters

    def initial(self) -> tuple[PvtGroupControlValues, PvtGroupControllerState]:
        return (
            self._current_values,
            PvtGroupControllerState.initial(self._time()),
        )

    def _string_warm(self, sensor_values: PvtGroupSensorValues):
        return (
            sensor_values.max_temperature_strings.temperature.value is not None
            and sensor_values.max_temperature_strings.temperature.value
            > self._parameters.recovery_activation_string_temperature
        )

    def _low_return_temperature(self, sensor_values: PvtGroupSensorValues):
        return (
            sensor_values.temperature_return.temperature.value
            < self._parameters.minimum_return_temperature
        )

    def _mix_open(self, sensor_values: PvtGroupSensorValues):
        return self._current_values.mix.setpoint.value > RECOVERY_MIX_UPPER_BOUND

    def _mix_closed(self, sensor_values: PvtGroupSensorValues):
        return self._current_values.mix.setpoint.value < RECOVERY_MIX_LOWER_BOUND

    def _set_mix_to_idle_position(self, sensor_values: PvtGroupSensorValues):
        self._current_values.mix.setpoint = Stamped(
            value=IDLE_MIX_POSITION, timestamp=self._time()
        )

    def _set_pump_to_minimum_dutypoint(self, sensor_values: PvtGroupSensorValues):
        self._current_values.pump.dutypoint = Stamped(
            value=self._parameters.minimum_pump_dutypoint, timestamp=self._time()
        )

    def _enable_warmup_mix(self, sensor_values: PvtGroupSensorValues):
        self._warmup_mix_controller.enable()

    def _disable_warmup_mix(self, sensor_values: PvtGroupSensorValues):
        self._warmup_mix_controller.disable()

    def _enable_pump_control(self, sensor_values: PvtGroupSensorValues):
        self._pump_controller.enable()

    def _disable_pump_control(self, sensor_values: PvtGroupSensorValues):
        self._pump_controller.disable()

    def _activate_pump(self, sensor_values: PvtGroupSensorValues):
        self._current_values.pump.on = Stamped(value=True, timestamp=self._time())

    def _deactivate_pump(self, sensor_values: PvtGroupSensorValues):
        self._current_values.pump.on = Stamped(value=False, timestamp=self._time())

    def control(
        self, sensor_values: PvtGroupSensorValues
    ) -> tuple[PvtGroupControlValues, PvtGroupControllerState]:
        self._state_machine.check_temperatures(sensor_values)
        self._control_warmup_mix(sensor_values)
        self._state_machine.check_mix(sensor_values)
        self._control_pump(sensor_values)

        return (
            self._current_values,
            PvtGroupControllerState(
                pvt_group_pump_controller=self._pump_controller.values(),
                pvt_group_warmup_mix_controller=self._warmup_mix_controller.values(),
            ),
        )

    def _control_warmup_mix(self, sensor_values: PvtGroupSensorValues):
        if self._warmup_mix_controller.enabled():
            self._current_values.mix.setpoint = Stamped(
                value=self._warmup_mix_controller(
                    sensor_values.temperature_return.temperature.value
                ),
                timestamp=self._time(),
            )

    def _control_pump(self, sensor_values: PvtGroupSensorValues):
        if self._pump_controller.enabled():
            self._current_values.pump.dutypoint = Stamped(
                value=self._pump_controller(
                    sensor_values.temperature_return.temperature.value
                ),
                timestamp=self._time(),
            )
