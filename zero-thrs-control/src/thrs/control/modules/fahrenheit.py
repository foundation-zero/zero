from datetime import datetime
from typing import cast

from pyparsing import Callable
from transitions import Machine, State
from thrs.classes.control import Control, ControlMode, ControlResult
from thrs.control.controllers import Controller
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Fahrenheit, Valve
from thrs.input_output.definitions.units import (
    Celsius,
    FahrenheitMode,
    FreeCoolingMode,
    Ratio,
    TankControlMode,
    Tuning,
)
from thrs.input_output.modules.fahrenheit import (
    FahrenheitControlValues,
    FahrenheitSensorValues,
)


class FahrenheitParameters(ThrsValues):
    waste_cooling_temperature: Celsius = 30
    waste_recovery_temperature: Celsius = 40
    fahrenheit_cooling_setpoint: Celsius = 17
    fahrenheit_hot_minimum: Celsius = 60
    fahrenheit_hot_trigger: Celsius = 65
    fahrenheit_cold_minimum: Celsius = 15
    fahrenheit_cold_trigger: Celsius = 17
    hot_mix_tuning: Tuning = (0.05, 0.001, 0)
    recovery_tuning: Tuning = (0.05, 0.001, 0)
    waste_cooling_tuning: Tuning = (0.05, 0.01, 0)
    free_cooling_enabled: bool = True


def _INITIAL_CONTROL_VALUES(timestamp) -> FahrenheitControlValues:
    return FahrenheitControlValues(
        fahrenheit_flowcontrol_waste=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        fahrenheit_mix_hot=Valve(
            setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=timestamp)
        ),
        fahrenheit_mix_waste=Valve(
            setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=timestamp)
        ),
        fahrenheit_chiller=Fahrenheit(
            enable=Stamped(value=False, timestamp=timestamp),
            mode=Stamped(value=FahrenheitMode.OFF, timestamp=timestamp),
            cooling_setpoint=Stamped(value=17.0, timestamp=timestamp),
            free_cooling_mode=Stamped(value=FreeCoolingMode.AUTO, timestamp=timestamp),
            available_seawater_temperature=Stamped(value=20.0, timestamp=timestamp),
            available_hot_temperature=Stamped(value=20.0, timestamp=timestamp),
            available_cold_temperature=Stamped(value=20.0, timestamp=timestamp),
            cold_minimum=Stamped(value=15.0, timestamp=timestamp),
            hot_minimum=Stamped(value=53.0, timestamp=timestamp),
            cold_hysteresis=Stamped(value=2.0, timestamp=timestamp),
            hot_hysteresis=Stamped(value=2.0, timestamp=timestamp),
            tank_control_mode=Stamped(value=TankControlMode.BOTH, timestamp=timestamp),
        ),
    )


class FahrenheitControlMode(ControlMode):
    mode: str


class FahrenheitControl(
    Control[
        FahrenheitSensorValues,
        FahrenheitControlValues,
        FahrenheitParameters,
        FahrenheitControlMode,
    ]
):
    def __init__(
        self, parameters: FahrenheitParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        self._states = [
            State(
                name="idle",
                on_enter=[self._disable_temperature_controllers],
            ),
            State(
                name="cooling",
                on_enter=[self._enable_temperature_controllers],
            ),
            State(
                name="free_cooling",
                on_enter=[
                    self._open_recovery_mix,
                    self._disable_recovery_mix,
                    self._set_free_cooling_setpoint,
                    self._disable_hot_mix,
                ],
            ),
        ]
        # Here the idea is that the Fahrenheit unit triggers the state machine, and mode switches thus depend on the input parameters for fahrenheit, and whether it's enabled.
        self._transitions = [
            {
                "trigger": "_check_fahrenheit_status",
                "source": ["idle", "free_cooling"],
                "dest": "cooling",
                "conditions": lambda sensor_values: sensor_values.fahrenheit_chiller.operating.value
                and not sensor_values.fahrenheit_chiller.free_cooling.value,  # TODO: check if we need to add error condition
            },
            {
                "trigger": "_check_fahrenheit_status",
                "source": ["cooling", "free_cooling"],
                "dest": "idle",
                "conditions": lambda sensor_values: not sensor_values.fahrenheit_chiller.operating.value,
            },
            {
                "trigger": "_check_free_cooling",
                "source": ["idle", "cooling"],
                "dest": "free_cooling",
                "conditions": lambda sensor_values: sensor_values.fahrenheit_chiller.operating.value
                and sensor_values.fahrenheit_chiller.free_cooling.value,
            },
        ]

        self._state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

        self._hot_mix_controller = Controller[Ratio, Celsius](
            self._current_values.fahrenheit_mix_hot.setpoint.value,
            0,
            lambda: self._parameters.hot_mix_tuning,
            self._time,
        )

        self._recovery_controller = Controller[Ratio, Celsius](
            self._current_values.fahrenheit_mix_waste.setpoint.value,
            0,
            lambda: self._parameters.recovery_tuning,
            self._time,
        )

        self._waste_cooling_controller = Controller[Ratio, Celsius](
            self._current_values.fahrenheit_flowcontrol_waste.setpoint.value,
            0,
            lambda: self._parameters.waste_cooling_tuning,
            self._time,
        )

    @property
    def parameters(self) -> FahrenheitParameters:
        return self._parameters

    def update_parameters(self, parameters: FahrenheitParameters) -> None:
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> FahrenheitControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return FahrenheitControlMode(mode=initial_mode)

    @property
    def mode(self) -> FahrenheitControlMode:
        mode: str = self.state  # type: ignore
        return FahrenheitControlMode(mode=mode)

    def initial(self) -> ControlResult[FahrenheitControlValues]:
        return ControlResult(self._time(), _INITIAL_CONTROL_VALUES(self._time()))

    def control(
        self, sensor_values: FahrenheitSensorValues
    ) -> ControlResult[FahrenheitControlValues]:
        self._update_fahrenheit_settings(sensor_values)
        # TODO: add triggers to transition between states
        self._control_temperature_controllers(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _control_temperature_controllers(self, sensor_values: FahrenheitSensorValues):
        self._current_values.fahrenheit_mix_hot.setpoint = Stamped(
            value=(
                self._hot_mix_controller(
                    sensor_values.fahrenheit_temperature_hot_supply.temperature.value
                )
            ),
            timestamp=self._time(),
        )
        self._current_values.fahrenheit_mix_waste.setpoint = Stamped(
            value=(
                self._waste_cooling_controller(
                    sensor_values.fahrenheit_temperature_waste_supply.temperature.value
                )
            ),
            timestamp=self._time(),
        )
        self._current_values.fahrenheit_flowcontrol_waste.setpoint = Stamped(
            value=(
                self._recovery_controller(
                    sensor_values.fahrenheit_temperature_waste_supply.temperature.value
                )
            ),
            timestamp=self._time(),
        )

    def _disable_hot_mix(self):
        self._hot_mix_controller.disable()

    def _disable_recovery_mix(self):
        self._recovery_controller.disable()

    def _disable_temperature_controllers(self, sensor_values: FahrenheitSensorValues):
        self._hot_mix_controller.disable()
        self._recovery_controller.disable()
        self._waste_cooling_controller.disable()

    def _enable_temperature_controllers(self, sensor_values: FahrenheitSensorValues):
        self._hot_mix_controller.enable()
        self._recovery_controller.enable()
        self._waste_cooling_controller.enable()

    def _set_free_cooling_setpoint(self):
        self._current_values.fahrenheit_chiller.cooling_setpoint = Stamped(
            value=self._parameters.fahrenheit_cooling_setpoint,  # TODO: should we set seawater temp = cooling setpoint?
            timestamp=self._time(),
        )

    def _open_recovery_mix(self):
        self._current_values.fahrenheit_flowcontrol_waste.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

    def _disable_fahrenheit(self, sensor_values: FahrenheitSensorValues):
        self._current_values.fahrenheit_chiller.enable = Stamped(
            value=False, timestamp=self._time()
        )
        self._current_values.fahrenheit_chiller.mode = Stamped(
            value=FahrenheitMode.OFF, timestamp=self._time()
        )

    def _enable_fahrenheit(self, sensor_values: FahrenheitSensorValues):
        self._current_values.fahrenheit_chiller.enable = Stamped(
            value=True, timestamp=self._time()
        )
        self._current_values.fahrenheit_chiller.mode = Stamped(
            value=FahrenheitMode.ON, timestamp=self._time()
        )

    def _update_fahrenheit_settings(self, sensor_values: FahrenheitSensorValues):
        if self._current_values.fahrenheit_chiller.free_cooling_mode.value != (
            FreeCoolingMode.AUTO
            if self._parameters.free_cooling_enabled
            else FreeCoolingMode.OFF
        ):
            self._current_values.fahrenheit_chiller.free_cooling_mode = Stamped(
                value=FreeCoolingMode.AUTO
                if self._parameters.free_cooling_enabled
                else FreeCoolingMode.OFF,
                timestamp=self._time(),
            )

        if (
            self._current_values.fahrenheit_chiller.available_seawater_temperature.value
            != sensor_values.fahrenheit_available_seawater_temperature.temperature.value
        ):
            self._current_values.fahrenheit_chiller.available_seawater_temperature = (
                Stamped(
                    value=cast(
                        Celsius, sensor_values.fahrenheit_available_seawater_temperature
                    ),
                    timestamp=self._time(),
                )
            )
        if (
            self._current_values.fahrenheit_chiller.available_hot_temperature.value
            != sensor_values.fahrenheit_available_hot_temperature.temperature.value
        ):
            self._current_values.fahrenheit_chiller.available_hot_temperature = Stamped(
                value=cast(Celsius, sensor_values.fahrenheit_available_hot_temperature),
                timestamp=self._time(),
            )
        if (
            self._current_values.fahrenheit_chiller.available_cold_temperature.value
            != sensor_values.fahrenheit_available_cold_temperature.temperature.value
        ):
            self._current_values.fahrenheit_chiller.available_cold_temperature = (
                Stamped(
                    value=cast(
                        Celsius, sensor_values.fahrenheit_available_cold_temperature
                    ),
                    timestamp=self._time(),
                )
            )
        if (
            self._current_values.fahrenheit_chiller.cold_minimum.value
            != self._parameters.fahrenheit_cold_minimum
        ):
            self._current_values.fahrenheit_chiller.cold_minimum = Stamped(
                value=self._parameters.fahrenheit_cold_minimum, timestamp=self._time()
            )
        if self._current_values.fahrenheit_chiller.cold_hysteresis.value != (
            self._parameters.fahrenheit_cold_trigger
            - self._parameters.fahrenheit_cold_minimum
        ):
            self._current_values.fahrenheit_chiller.cold_hysteresis = Stamped(
                value=self._parameters.fahrenheit_cold_trigger
                - self._parameters.fahrenheit_cold_minimum,
                timestamp=self._time(),
            )
        if (
            self._current_values.fahrenheit_chiller.hot_minimum.value
            != self._parameters.fahrenheit_hot_minimum
        ):
            self._current_values.fahrenheit_chiller.hot_minimum = Stamped(
                value=self._parameters.fahrenheit_hot_minimum, timestamp=self._time()
            )
        if self._current_values.fahrenheit_chiller.hot_hysteresis.value != (
            self._parameters.fahrenheit_hot_trigger
            - self._parameters.fahrenheit_hot_minimum
        ):
            self._current_values.fahrenheit_chiller.hot_hysteresis = Stamped(
                value=self._parameters.fahrenheit_hot_trigger
                - self._parameters.fahrenheit_hot_minimum,
                timestamp=self._time(),
            )
