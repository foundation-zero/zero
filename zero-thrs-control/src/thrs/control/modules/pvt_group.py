from datetime import datetime
from typing import Callable

from pydantic import model_validator
from transitions import Machine, State
from thrs.classes.control import Control, ControlResult
from thrs.control.controllers import Controller
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions import control
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, Ratio, Tuning


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


def _INITIAL_CONTROL_VALUES(timestamp) -> PvtGroupControlValues:
    return PvtGroupControlValues(
        pump=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        mix=Valve(setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)),
    )


class PvtGroupControlMode(ThrsValues):
    mode: str


class PvtGroupControl(
    Control[
        PvtGroupSensorValues,
        PvtGroupControlValues,
        PvtGroupParameters,
        PvtGroupControlMode,
    ]
):
    def __init__(
        self, parameters: PvtGroupParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )
        self._states = [
            State(name="idle", on_enter=self._set_mix_to_a),
            State(
                name="recovery",
                on_enter=[
                    self._enable_warmup_mix,
                    self._enable_pump_control,
                    self._activate_pump,
                ],
                on_exit=[
                    self._disable_warmup_mix,
                    self._disable_pump_control,
                    self._deactivate_pump,
                ],
            ),
        ]

        self._transitions = [
            {
                "trigger": "_check_temperatures",
                "source": "idle",
                "dest": "recovery",
                "conditions": "_string_warm",
            },
            {
                "trigger": "_check_temperatures",
                "source": "recovery",
                "dest": "idle",
                "conditions": "_low_return_temperature",
            },
        ]

        self._state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

        self._warmup_mix_controller = Controller[Ratio, Celsius](
            self._current_values.mix.setpoint.value,
            lambda: self._parameters.warmup_temperature,
            lambda: self._parameters.warmup_mix_tuning,
            self._time,
        )

        self._pump_controller = Controller[Ratio, Celsius](
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
    def current_values(self) -> PvtGroupControlValues:
        return self._current_values

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> PvtGroupControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return PvtGroupControlMode(mode=initial_mode)

    @property
    def mode(self) -> PvtGroupControlMode:
        mode: str = self.state  # type: ignore
        return PvtGroupControlMode(mode=mode)

    def update_parameters(self, parameters: PvtGroupParameters):
        self._parameters = parameters

    def initial(self) -> ControlResult[PvtGroupControlValues]:
        return ControlResult(self._time(), _INITIAL_CONTROL_VALUES(self._time()))

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

    def _set_mix_to_a(self, sensor_values: PvtGroupSensorValues):
        self._current_values.mix.setpoint = Stamped(
            value=Valve.MIXING_B_TO_AB, timestamp=self._time()
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
    ) -> ControlResult[PvtGroupControlValues]:
        self._check_temperatures(sensor_values)  # type: ignore
        self._control_warmup_mix(sensor_values)
        self._control_pump(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _control_warmup_mix(self, sensor_values: PvtGroupSensorValues):
        self._current_values.mix.setpoint = Stamped(
            value=self._warmup_mix_controller(
                sensor_values.temperature_return.temperature.value
            ),
            timestamp=self._time(),
        )

    def _control_pump(self, sensor_values: PvtGroupSensorValues):
        self._current_values.pump.dutypoint = Stamped(
            value=self._pump_controller(
                sensor_values.temperature_return.temperature.value
            ),
            timestamp=self._time(),
        )
