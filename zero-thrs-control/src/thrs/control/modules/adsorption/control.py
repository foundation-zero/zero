from collections.abc import Callable
from datetime import datetime

from statemachine import State, StateChart

from thrs.classes.control import Control
from thrs.control.controllers import PidController
from thrs.control.modules.adsorption.io import (
    AdsorptionControlValues,
    AdsorptionSensorValues,
)
from thrs.control.modules.adsorption.state import (
    AdsorptionControllerState,
    AdsorptionControlMode,
    AdsorptionParameters,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.units import (
    AdsorptionChillerMode,
    Celsius,
    FreeCoolingMode,
    Ratio,
)
from thrs.orchestration.module import ModuleDescription


class _AdsorptionStateMachine(StateChart["AdsorptionControl"]):
    """Each event takes the first of its transitions whose condition holds.

    The adsorption unit decides when it runs, so the modes follow the chiller's
    reported state.
    """

    # An error in a guard or action raises instead of becoming an unhandled event.
    catch_errors_as_events = False

    idle = State(initial=True, enter="_disable_temperature_controllers")
    cooling = State(enter="_enable_temperature_controllers")
    free_cooling = State(
        enter=[
            "_open_recovery_mix",
            "_disable_recovery_mix",
            "_set_free_cooling_setpoint",
            "_disable_hot_mix",
        ]
    )

    # TODO: check if we need to add error conditions
    check_adsorption_status = cooling.from_(
        idle, free_cooling, cond="_chiller_operating and not _chiller_free_cooling"
    ) | idle.from_(cooling, free_cooling, cond="not _chiller_operating")
    check_free_cooling = free_cooling.from_(
        idle, cooling, cond="_chiller_operating and _chiller_free_cooling"
    )


class AdsorptionControl(
    Control[
        AdsorptionSensorValues,
        AdsorptionControlValues,
        AdsorptionParameters,
        AdsorptionControlMode,
        AdsorptionControllerState,
    ]
):
    def __init__(
        self,
        parameters: AdsorptionParameters,
        time_fn: Callable[[], datetime],
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = AdsorptionControlValues.initial(self._time())

        # Starting with a mode set skips idle's enter actions: the first outputs are
        # the initial control values.
        self._state: str = _AdsorptionStateMachine.idle.value
        self._state_machine = _AdsorptionStateMachine(model=self, state_field="_state")
        self._init_controllers()

    def _init_controllers(self):
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

    @property
    def mode(self) -> AdsorptionControlMode:
        return AdsorptionControlMode(mode=self._state)

    def initial(self) -> tuple[AdsorptionControlValues, AdsorptionControllerState]:
        timestamp = self._time()
        return (
            AdsorptionControlValues.initial(timestamp),
            AdsorptionControllerState.initial(timestamp),
        )

    def control(
        self, sensor_values: AdsorptionSensorValues
    ) -> tuple[AdsorptionControlValues, AdsorptionControllerState]:
        self._update_adsorption_inputs(sensor_values)
        self._state_machine.check_adsorption_status(sensor_values)
        controller_state = self._control_temperature_controllers(sensor_values)

        return (self._current_values, controller_state)

    def _control_temperature_controllers(
        self, sensor_values: AdsorptionSensorValues
    ) -> AdsorptionControllerState:
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

        return AdsorptionControllerState(
            adsorption_hot_mix_controller=self._hot_mix_controller.values(),
            adsorption_recovery_controller=self._recovery_controller.values(),
            adsorption_waste_cooling_controller=self._waste_cooling_controller.values(),
            parameters=self._parameters,
            control_mode=self.mode,
        )

    def _chiller_operating(self, sensor_values: AdsorptionSensorValues) -> bool:
        return sensor_values.adsorption_chiller.operating.value

    def _chiller_free_cooling(self, sensor_values: AdsorptionSensorValues) -> bool:
        return sensor_values.adsorption_chiller.free_cooling.value

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
            value=AdsorptionChillerMode.ON, timestamp=self._time()
        )

        self._current_values.adsorption_chiller.free_cooling_mode = Stamped(
            value=FreeCoolingMode.AUTO
            if self._parameters.free_cooling_enabled
            else FreeCoolingMode.OFF,
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
    AdsorptionControllerState,
    AdsorptionAlarms,
)
