from datetime import datetime
from typing import Callable, Literal

from transitions import Machine, State
from thrs.classes.control import Control, ControlResult
from thrs.control.controllers import Controller, FlowBalanceController
from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.control import Pcm, Pump, Valve
from thrs.input_output.definitions.units import Celsius, LMin, Ratio, Tuning
from thrs.input_output.modules.pcm import PcmControlValues, PcmSensorValues


class PcmParameters(ThrsModel):
    pcm_discharge_flow: LMin = 5
    pcm_charge_flow: LMin = 5
    minimum_charging_dt: Celsius = 2
    pump_tuning: Tuning = (0.01, 0.001, 0)
    module_1_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    module_2_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    module_3_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    module_4_flow_balance_tuning: Tuning = (0.01, 0.001, 0)


_ZERO_TIME = datetime.fromtimestamp(0)
_INITIAL_CONTROL_VALUES = PcmControlValues(
    pcm_pump=Pump(
        dutypoint=Stamped(value=0, timestamp=_ZERO_TIME),
        on=Stamped(value=False, timestamp=_ZERO_TIME),
    ),
    pcm_switch_charging_return=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    pcm_flowcontrol_module_1=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_flowcontrol_module_2=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_flowcontrol_module_3=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_flowcontrol_module_4=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_switch_discharging=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    pcm_switch_charging_supply=Valve(
        setpoint=Stamped(value=Valve.CLOSED, timestamp=_ZERO_TIME)
    ),
    pcm_switch_consumers=Valve(
        setpoint=Stamped(value=Valve.OPEN, timestamp=_ZERO_TIME)
    ),
    pcm_module_1=Pcm(on=Stamped(value=False, timestamp=_ZERO_TIME)),
)


class PcmControl(Control[PcmSensorValues, PcmControlValues, PcmParameters]):
    def __init__(
        self, parameters: PcmParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)

        self._states = [
            State(
                name="supplying",
                on_enter=[
                    self._set_valves_to_supplying,
                    self._set_flow_balancing_to_supplying,
                ],
            ),
            State(
                name="charging",
                on_enter=[
                    self._set_valves_to_charging,
                    self._set_flow_balancing_to_charging,
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
            ),
        ]

        self.pcm_state_machine = Machine(
            model=self, states=self._states, initial="idle"
        )

        self._pump_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.pcm_pump.dutypoint.value,
            0,
            parameters.pump_tuning,
            self._time,
        )

        self.module_1_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.pcm_flowcontrol_module_1.setpoint.value,
            0,
            parameters.module_1_flow_balance_tuning,
            self._time,
        )

        self.module_2_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.pcm_flowcontrol_module_2.setpoint.value,
            0,
            parameters.module_2_flow_balance_tuning,
            self._time,
        )

        self.module_3_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.pcm_flowcontrol_module_3.setpoint.value,
            0,
            parameters.module_3_flow_balance_tuning,
            self._time,
        )

        self.module_4_flow_controller = Controller[Ratio, LMin](
            _INITIAL_CONTROL_VALUES.pcm_flowcontrol_module_4.setpoint.value,
            0,
            parameters.module_4_flow_balance_tuning,
            self._time,
        )

        self._flow_balance_controller = FlowBalanceController(
            [
                self._current_values.pcm_flowcontrol_module_1,
                self._current_values.pcm_flowcontrol_module_2,
                self._current_values.pcm_flowcontrol_module_3,
                self._current_values.pcm_flowcontrol_module_4,
            ],
            [
                self.module_1_flow_controller,
                self.module_2_flow_controller,
                self.module_3_flow_controller,
                self.module_4_flow_controller,
            ],
            self._current_values.pcm_pump,
            self._pump_flow_controller,
            self._time,
        )

    @property
    def parameters(self) -> PcmParameters:
        return self._parameters

    @staticmethod
    def modes() -> list[str]:
        return ["supplying", "charging", "boosting", "idle"]

    @staticmethod
    def initial_mode() -> str:
        return "idle"

    @property
    def mode(self) -> Literal["supplying", "charging", "boosting", "idle"]:
        return self.state  # type: ignore

    def initial(self) -> ControlResult[PcmControlValues]:
        return ControlResult(self._time(), self._current_values)

    def control(self, sensor_values: PcmSensorValues) -> ControlResult:
        self._control_flow_balance(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _set_flow_balancing_to_supplying(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller.set_pump(self._current_values.pcm_pump)
        self._flow_balance_controller.enable(
            [
                sensor_values.pcm_module_1.charged.value,
                sensor_values.pcm_module_2.charged.value,
                sensor_values.pcm_module_3.charged.value,
                sensor_values.pcm_module_4.charged.value,
            ]
        )
        self._flow_balance_controller.set_setpoint(self.parameters.pcm_discharge_flow)

    def _set_supplying_flow_setpoints(self, sensor_values: PcmSensorValues):
        charged_modules = [
            sensor_values.pcm_module_1.charged.value,
            sensor_values.pcm_module_2.charged.value,
            sensor_values.pcm_module_3.charged.value,
            sensor_values.pcm_module_4.charged.value,
        ]

        self._flow_balance_controller.set_active_valves(charged_modules)
        self._flow_balance_controller.set_setpoints(
            [
                self.parameters.pcm_discharge_flow if charged else 0.0
                for charged in charged_modules
            ]
        )

    def _set_flow_balancing_to_charging(self):
        self._flow_balance_controller.set_pump(None)
        self._flow_balance_controller.enable([True, True, True, True])
        self._flow_balance_controller.set_setpoint(self.parameters.pcm_charge_flow)

    # TODO: need timer here?

    def _set_charging_flow_setpoints(self, sensor_values: PcmSensorValues):
        charging_modules = [
            (
                temp_out
                - sensor_values.pcm_temperature_producers_supply.temperature.value
            )
            > self.parameters.minimum_charging_dt
            for temp_out in [
                sensor_values.pcm_temperature_module_1_out.temperature.value,
                sensor_values.pcm_temperature_module_2_out.temperature.value,
                sensor_values.pcm_temperature_module_3_out.temperature.value,
                sensor_values.pcm_temperature_module_4_out.temperature.value,
            ]
        ]

        self._flow_balance_controller.set_active_valves(charging_modules)
        self._flow_balance_controller.set_setpoints(
            [
                self.parameters.pcm_charge_flow if charging else 0.0
                for charging in charging_modules
            ]
        )

    def _disable_flow_balancing(self):
        self._flow_balance_controller.disable()

    def _control_flow_balance(self, sensor_values: PcmSensorValues):
        self._flow_balance_controller(
            [
                sensor_values.pcm_flow_module_1.flow.value,
                sensor_values.pcm_flow_module_2.flow.value,
                sensor_values.pcm_flow_module_3.flow.value,
                sensor_values.pcm_flow_module_4.flow.value,
            ]
        )

    def _set_valves_to_idle(self):
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

    def _set_valves_to_supplying(self):
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

    def _set_valves_to_charging(self):
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

    def _set_valves_to_boosting(self):
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
