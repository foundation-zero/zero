from datetime import datetime
from functools import partial
from typing import Callable, Literal

from pydantic import BaseModel
from transitions import Machine, State
from classes.control import Control, ControlResult
from control.controllers import PumpFlowController
from input_output.base import Stamped
from input_output.definitions.control import Pcm, Pump, Valve
from input_output.definitions.units import LMin
from input_output.modules.pcm import PcmControlValues, PcmSensorValues


class PcmParameters(BaseModel):
    supplying_pump_flow: LMin = 60
    boosting_pump_flow: LMin = 20


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


class PcmControl(Control[PcmSensorValues, PcmControlValues]):
    def __init__(self, parameters: PcmParameters) -> None:
        self._parameters = parameters

        states = [
            State(
                name="supplying",
                on_enter=[
                    self._set_valves_to_discharge,
                    partial(self._enable_pump, lambda : self._parameters.supplying_pump_flow),
                ],
            ),
            State(
                name="charging",
                on_enter=[self._set_valves_to_charge, self._disable_pump],
            ),
            State(
                name="boosting",
                on_enter=[
                    self._set_valves_to_boosting,
                    partial(self._enable_pump, lambda : self._parameters.boosting_pump_flow),
                ],
            ),
            State(name="idle", on_enter=[self._set_valves_to_idle, self._disable_pump]),
        ]

        self.machine = Machine(model=self, states=states, initial="idle")
        self._pump_flow_controller = PumpFlowController(
            _INITIAL_CONTROL_VALUES.pcm_pump.dutypoint.value, 0
        )
        self.machine = Machine(model=self, states=states, initial="idle")
        self._pump_flow_controller = PumpFlowController(
            _INITIAL_CONTROL_VALUES.pcm_pump.dutypoint.value, 0
        )

        self._current_values = _INITIAL_CONTROL_VALUES.model_copy(deep=True)
        self._time = datetime.now()

    @property
    def mode(self) -> Literal["supplying", "charging", "boosting", "idle"]:
        return self.state  # type: ignore

    def initial(self, time: datetime) -> ControlResult[PcmControlValues]:
        return ControlResult(time, self._current_values)

    def _set_valves_to_idle(self):
        self._current_values.pcm_switch_charging_return.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )
        self._current_values.pcm_switch_discharging.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )
        self._current_values.pcm_switch_charging_supply.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )
        self._current_values.pcm_switch_consumers.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )

    def _set_valves_to_discharge(self):
        self._current_values.pcm_switch_charging_return.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )
        self._current_values.pcm_switch_discharging.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )
        self._current_values.pcm_switch_charging_supply.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )
        self._current_values.pcm_switch_consumers.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )

    def _set_valves_to_charge(self):
        self._current_values.pcm_switch_charging_return.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )
        self._current_values.pcm_switch_discharging.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )
        self._current_values.pcm_switch_charging_supply.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )
        self._current_values.pcm_switch_consumers.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )

    def _set_valves_to_boosting(self):
        self._current_values.pcm_switch_charging_return.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )
        self._current_values.pcm_switch_discharging.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )
        self._current_values.pcm_switch_charging_supply.setpoint = Stamped(
            value=Valve.OPEN, timestamp=self._time
        )
        self._current_values.pcm_switch_consumers.setpoint = Stamped(
            value=Valve.CLOSED, timestamp=self._time
        )

    def _disable_pump(self):
        if self._current_values.pcm_pump.on.value:
            self._current_values.pcm_pump.on = Stamped(
                value=False, timestamp=self._time
            )
            self._pump_flow_controller.disable()

    def _enable_pump(self, setpoint: Callable[[], LMin]):
        if not self._current_values.pcm_pump.on.value:
            self._current_values.pcm_pump.on = Stamped(value=True, timestamp=self._time)
            self._pump_flow_controller.enable()
        self._pump_flow_controller.setpoint = setpoint()

    def _control_pump(self, sensor_values: PcmSensorValues):
        self._current_values.pcm_pump.dutypoint = Stamped(
            value=self._pump_flow_controller(
                sensor_values.pcm_pump.flow.value,
                self._time,
            ),
            timestamp=self._time,
        )

    def control(self, sensor_values: PcmSensorValues, time: datetime) -> ControlResult:
        self._time = time

        self._control_pump(sensor_values)

        return ControlResult(time, self._current_values)
