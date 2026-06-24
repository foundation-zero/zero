from datetime import datetime
from typing import Callable

from pydantic import model_validator
from transitions import Machine, State

from thrs.classes.control import Control, ControlMode
from thrs.control.base import ModuleDescription
from thrs.control.controllers import PidController
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import AdsorptionChiller, Valve
from thrs.input_output.definitions.units import (
    ADSORPTION_CHILLER_MODE_OFF,
    ADSORPTION_CHILLER_MODE_ON,
    FREE_COOLING_MODE_AUTO,
    TANK_CONTROL_MODE_BOTH,
    Celsius,
    Ratio,
    Tuning,
)
from thrs.input_output.modules.adsorption import (
    AdsorptionControlValues,
    AdsorptionSensorValues,
)


class AdsorptionParameters(ThrsValues):
    chiller_enabled: bool = True
    waste_cooling_temperature_setpoint: Celsius = 35.0
    waste_recovery_temperature_setpoint: Celsius = 34.0
    hot_supply_temperature_setpoint: Celsius = 60.0
    adsorption_cooling_setpoint: Celsius = 17.0
    adsorption_hot_minimum: Celsius = 50.0
    adsorption_hot_trigger: Celsius = 55.0
    adsorption_cold_minimum: Celsius = 10.0
    adsorption_cold_trigger: Celsius = 17.0
    hot_mix_tuning: Tuning = (0.05, 0.001, 0)
    recovery_tuning: Tuning = (0.05, 0.001, 0)
    waste_cooling_tuning: Tuning = (0.05, 0.01, 0)
    free_cooling_enabled: bool = False

    @model_validator(mode="after")
    def check_temperature_setpoints(self):
        if self.adsorption_hot_trigger <= self.adsorption_hot_minimum:
            raise ValueError(
                "Hot trigger temperature must be greater than hot minimum temperature"
            )
        if self.adsorption_cold_trigger <= self.adsorption_cold_minimum:
            raise ValueError(
                "Cold trigger temperature must be greater than cold minimum temperature"
            )
        return self


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> AdsorptionControlValues:
    return AdsorptionControlValues(
        adsorption_flowcontrol_waste=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        adsorption_mix_hot=Valve(
            setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=timestamp)
        ),
        adsorption_mix_waste=Valve(
            setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=timestamp)
        ),
        adsorption_switch_dhw=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        adsorption_chiller=AdsorptionChiller(
            enable=Stamped(value=False, timestamp=timestamp),
            mode=Stamped(value=ADSORPTION_CHILLER_MODE_OFF, timestamp=timestamp),
            cooling_setpoint=Stamped(value=17.0, timestamp=timestamp),
            free_cooling_mode=Stamped(
                value=FREE_COOLING_MODE_AUTO, timestamp=timestamp
            ),
            available_seawater_temperature=Stamped(value=20.0, timestamp=timestamp),
            available_hot_temperature=Stamped(value=20.0, timestamp=timestamp),
            available_cold_temperature=Stamped(value=20.0, timestamp=timestamp),
            cold_minimum=Stamped(value=15.0, timestamp=timestamp),
            hot_minimum=Stamped(value=53.0, timestamp=timestamp),
            cold_hysteresis=Stamped(value=2.0, timestamp=timestamp),
            hot_hysteresis=Stamped(value=2.0, timestamp=timestamp),
            tank_control_mode=Stamped(
                value=TANK_CONTROL_MODE_BOTH, timestamp=timestamp
            ),
        ),
    )


class AdsorptionControlMode(ControlMode):
    mode: str


class AdsorptionControllerValues(ThrsValues):
    control_mode: AdsorptionControlMode


class AdsorptionControl(
    Control[
        AdsorptionSensorValues,
        AdsorptionControlValues,
        AdsorptionParameters,
        AdsorptionControllerValues,
    ]
):
    def __init__(
        self, parameters: AdsorptionParameters, time_fn: Callable[[], datetime]
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
        # Here the idea is that the Adsorption unit triggers the state machine, and mode switches thus depend on the input parameters for adsorption, and whether it's enabled.
        self._transitions = [
            {
                "trigger": "_check_adsorption_status",
                "source": ["idle", "free_cooling"],
                "dest": "cooling",
                "conditions": lambda sensor_values: (
                    sensor_values.adsorption_chiller.operating.value
                    and not sensor_values.adsorption_chiller.free_cooling.value
                ),  # TODO: check if we need to add error condition
            },
            {
                "trigger": "_check_adsorption_status",
                "source": ["cooling", "free_cooling"],
                "dest": "idle",
                "conditions": lambda sensor_values: (
                    not sensor_values.adsorption_chiller.operating.value
                ),  # TODO: check if we need to add error condition
            },
            {
                "trigger": "_check_free_cooling",
                "source": ["idle", "cooling"],
                "dest": "free_cooling",
                "conditions": lambda sensor_values: (
                    sensor_values.adsorption_chiller.operating.value
                    and sensor_values.adsorption_chiller.free_cooling.value
                ),
            },
        ]

        self._state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

        self._hot_mix_controller = PidController[Ratio, Celsius](
            self._current_values.adsorption_mix_hot.setpoint.value,
            lambda: self._parameters.hot_supply_temperature_setpoint,
            lambda: self._parameters.hot_mix_tuning,
            self._time,
        )

        self._recovery_controller = PidController[Ratio, Celsius](
            self._current_values.adsorption_flowcontrol_waste.setpoint.value,
            lambda: self._parameters.waste_recovery_temperature_setpoint,
            lambda: self._parameters.recovery_tuning,
            self._time,
        )

        self._waste_cooling_controller = PidController[Ratio, Celsius](
            self._current_values.adsorption_mix_waste.setpoint.value,
            lambda: self._parameters.waste_cooling_temperature_setpoint,
            lambda: self._parameters.waste_cooling_tuning,
            self._time,
        )

    @property
    def parameters(self) -> AdsorptionParameters:
        return self._parameters

    def update_parameters(self, parameters: AdsorptionParameters) -> None:
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    def initial(self) -> tuple[AdsorptionControlValues, AdsorptionControllerValues]:
        initial_mode: str = self._state_machine.initial  # type: ignore

        return (
            _INITIAL_CONTROL_VALUES(self._time()),
            AdsorptionControllerValues(
                control_mode=AdsorptionControlMode(mode=initial_mode)
            ),
        )

    def control(
        self, sensor_values: AdsorptionSensorValues
    ) -> tuple[AdsorptionControlValues, AdsorptionControllerValues]:
        self._update_adsorption_inputs(sensor_values)
        self._check_adsorption_status(sensor_values)  # type: ignore
        self._control_temperature_controllers(sensor_values)
        mode: str = self.state  # type: ignore

        return (
            self._current_values,
            AdsorptionControllerValues(control_mode=AdsorptionControlMode(mode=mode)),
        )

    def _control_temperature_controllers(self, sensor_values: AdsorptionSensorValues):
        self._current_values.adsorption_mix_hot.setpoint = Stamped(
            value=(
                self._hot_mix_controller(
                    sensor_values.adsorption_temperature_hot_supply.temperature.value
                )
            ),
            timestamp=self._time(),
        )
        self._current_values.adsorption_mix_waste.setpoint = Stamped(
            value=(
                self._waste_cooling_controller(
                    sensor_values.adsorption_chiller.temperature_waste_in.value
                )
            ),
            timestamp=self._time(),
        )
        self._current_values.adsorption_flowcontrol_waste.setpoint = Stamped(
            value=(
                self._recovery_controller(
                    sensor_values.adsorption_chiller.temperature_waste_out.value
                )
            ),
            timestamp=self._time(),
        )

    def _disable_hot_mix(self):
        self._hot_mix_controller.disable()

    def _disable_recovery_mix(self):
        self._recovery_controller.disable()

    def _disable_temperature_controllers(self, sensor_values: AdsorptionSensorValues):
        self._hot_mix_controller.disable()
        self._recovery_controller.disable()
        self._waste_cooling_controller.disable()

    def _enable_temperature_controllers(self, sensor_values: AdsorptionSensorValues):
        self._hot_mix_controller.enable()
        self._recovery_controller.enable()
        self._waste_cooling_controller.enable()

    def _set_free_cooling_setpoint(self):
        self._current_values.adsorption_chiller.cooling_setpoint = Stamped(
            value=self._parameters.adsorption_cooling_setpoint,  # TODO: should we set seawater temp = cooling setpoint?
            timestamp=self._time(),
        )

    def _open_recovery_mix(self):
        self._current_values.adsorption_flowcontrol_waste.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time()
        )

    def _update_adsorption_inputs(self, sensor_values: AdsorptionSensorValues):
        self._current_values.adsorption_chiller.enable = Stamped(
            value=self._parameters.chiller_enabled, timestamp=self._time()
        )

        self._current_values.adsorption_chiller.mode = Stamped(
            value=ADSORPTION_CHILLER_MODE_ON, timestamp=self._time()
        )

        self._current_values.adsorption_chiller.free_cooling_mode = Stamped(
            value=FREE_COOLING_MODE_AUTO
            if self._parameters.free_cooling_enabled
            else 0,
            timestamp=self._time(),
        )

        self._current_values.adsorption_chiller.available_seawater_temperature = Stamped(
            value=sensor_values.adsorption_available_seawater_temperature.temperature.value,
            timestamp=self._time(),
        )

        self._current_values.adsorption_chiller.available_hot_temperature = Stamped(
            value=sensor_values.adsorption_available_hot_temperature.temperature.value,
            timestamp=self._time(),
        )

        self._current_values.adsorption_chiller.available_cold_temperature = Stamped(
            value=sensor_values.adsorption_available_cold_temperature.temperature.value,
            timestamp=self._time(),
        )
        self._current_values.adsorption_chiller.cold_minimum = Stamped(
            value=self._parameters.adsorption_cold_minimum, timestamp=self._time()
        )

        self._current_values.adsorption_chiller.cold_hysteresis = Stamped(
            value=self._parameters.adsorption_cold_trigger
            - self._parameters.adsorption_cold_minimum,
            timestamp=self._time(),
        )
        self._current_values.adsorption_chiller.hot_minimum = Stamped(
            value=self._parameters.adsorption_hot_minimum, timestamp=self._time()
        )
        self._current_values.adsorption_chiller.hot_hysteresis = Stamped(
            value=self._parameters.adsorption_hot_trigger
            - self._parameters.adsorption_hot_minimum,
            timestamp=self._time(),
        )


class AdsorptionAlarms(BaseAlarms):
    pass


ADSORPTION_MODULE_DESCRIPTION = ModuleDescription(
    AdsorptionSensorValues,
    AdsorptionControlValues,
    AdsorptionParameters,
    AdsorptionControl,
    AdsorptionControllerValues,
    AdsorptionAlarms,
)
