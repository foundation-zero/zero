from datetime import datetime
from typing import Callable

from transitions import Machine, State
from thrs.classes.control import Control, ControlResult
from thrs.control.controllers import Controller, FlowDistributionController
from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.units import Celsius, LMin, Ratio, Tuning
from thrs.input_output.modules.boilers import BoilersControlValues, BoilersSensorValues

from thrs.input_output.definitions import control


class BoilersParameters(ThrsModel):
    heatpump_flow_setpoint: LMin = 25
    boosting_temperature_setpoint: Celsius = 55
    tank_temperature_setpoint: Celsius = 50
    propdrive_shore_flow_ratio_setpoint: Ratio = 0.5
    converters_flow_ratio_setpoint: Ratio = 0.5
    tank1_disable: bool = False
    tank2_disable: bool = False
    tank3_disable: bool = False
    pump_temperature_tuning: Tuning = (-0.01, -0.001, 0.0)
    pump_flow_tuning: Tuning = (0.01, 0.001, 0.0)
    converters_flow_tuning: Tuning = (0.01, 0.001, 0.0)
    propdrive_shore_flow_tuning: Tuning = (0.01, 0.001, 0.0)


_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = BoilersControlValues(
    boilers_pump=control.Pump(
        dutypoint=Stamped(value=0.0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    boilers_heatpump=control.HeatPump(),
    boilers_flowcontrol_converters=control.Valve(
        setpoint=Stamped(value=0.5, timestamp=_ZERO_TIME)
    ),
    boilers_flowcontrol_propdrive_shore=control.Valve(
        setpoint=Stamped(value=0.5, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank3_fill=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank3_boosting_return=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank3_empty=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank3_boosting_supply=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank2_fill=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank2_boosting_return=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank2_empty=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank2_boosting_supply=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank1_fill=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank1_boosting_return=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank1_empty=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_tank1_boosting_supply=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_low_temperature=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_heatpump=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
    boilers_switch_high_temperature=control.Valve(
        setpoint=Stamped(value=0.0, timestamp=_ZERO_TIME)
    ),
)


class BoilersControl(
    Control[BoilersSensorValues, BoilersControlValues, BoilersParameters]
):
    def __init__(
        self, parameters: BoilersParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)

        self._states = [
            State(
                name="idle",
                on_enter=[self._deactivate_pump],
                on_exit=[self._activate_pump],
            ),
            State(
                name="boosting_low_temperature",
                on_enter=[
                    self._set_valves_to_boosting_low_temperature,
                    self._enable_pump_temperature_control,
                ],
            ),
            State(
                name="boosting_high_temperature",
                on_enter=[
                    self._set_valves_to_boosting_high_temperature,
                    self._enable_pump_temperature_control,
                ],
            ),
            State(
                name="boosting_heatpump",
                on_enter=[
                    self._set_valves_to_boosting_heatpump,
                    self._enable_pump_flow_control,
                ],
            ),
        ]
        self._transitions = []
        self.boilers_state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

        self._pump_temperature_controller = Controller[Ratio, Celsius](
            _INITIAL_CONTROL_VALUES.boilers_pump.dutypoint.value,
            0,
            parameters.pump_temperature_tuning,
            self._time,
        )

        self._pump_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.boilers_pump.dutypoint.value,
            0,
            parameters.pump_flow_tuning,
            self._time,
        )

        self._propdrive_shore_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.boilers_flowcontrol_propdrive_shore.setpoint.value,
            0,
            parameters.propdrive_shore_flow_tuning,
            self._time,
        )

        self._converters_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.boilers_flowcontrol_converters.setpoint.value,
            0,
            parameters.converters_flow_tuning,
            self._time,
        )
        self._flow_distribution_controller = FlowDistributionController(
            [
                self._current_values.boilers_flowcontrol_propdrive_shore,
                self._current_values.boilers_flowcontrol_converters,
            ],
            [
                self._propdrive_shore_flow_controller,
                self._converters_flow_controller,
            ],
        )
        self._flow_distribution_controller.set_active_valves([True, True])

    def initial(self) -> ControlResult[BoilersControlValues]:
        return ControlResult(self._time(), self._current_values)

    def _control_flow_distribution(self, sensor_values: BoilersSensorValues):
        self._flow_distribution_controller.set_ratios(
            [
                self._parameters.propdrive_shore_flow_ratio_setpoint,
                self._parameters.converters_flow_ratio_setpoint,
            ]
        )
        self._flow_distribution_controller(
            [
                sensor_values.boilers_flow_propdrive_shore.flow.value,
                sensor_values.boilers_flow_converters.flow.value,
            ]
        )

    def _set_valves_to_boosting_low_temperature(self):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _set_valves_to_boosting_high_temperature(self):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )

    def _set_valves_to_boosting_heatpump(self):
        self._current_values.boilers_switch_low_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_high_temperature.setpoint = Stamped(
            value=0.0, timestamp=self._time()
        )
        self._current_values.boilers_switch_heatpump.setpoint = Stamped(
            value=1.0, timestamp=self._time()
        )

    def _activate_pump(self):
        self._current_values.boilers_pump.on = Stamped(
            value=True, timestamp=self._time()
        )

    def _deactivate_pump(self):
        self._current_values.boilers_pump.on = Stamped(
            value=False, timestamp=self._time()
        )

    def _enable_pump_temperature_control(self):
        self._pump_temperature_controller.enable()

    def _disable_pump_temperature_control(self):
        self._pump_temperature_controller.disable()

    def _enable_pump_flow_control(self):
        self._pump_flow_controller.enable()

    def _disable_pump_flow_control(self):
        self._pump_flow_controller.disable()
