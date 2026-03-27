from datetime import datetime
from typing import Callable

from transitions import Machine

from thrs.classes.control import Control, ControlResult

from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.modules.lt2 import Lt2ControlValues, Lt2SensorValues


class Lt2ControlMode(ThrsValues):
    mode: str


class Lt2Parameters(ThrsValues):
    pass


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> Lt2ControlValues:
    return Lt2ControlValues(
        lt2_pump_aft=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        lt2_pump_fwd=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        lt2_pump_ugrid=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        lt2_mix_fwd=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        lt2_mix_aft=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        lt2_mix_ugrid=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        lt2_mix_recovery=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        lt2_mix_exchanger=Valve(
            setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=timestamp)
        ),
        lt2_switch_aft4=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        lt2_switch_aft3=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        lt2_switch_aft2=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        lt2_switch_aft1=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        lt2_switch_fwd2=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        lt2_switch_fwd1=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        lt2_switch_ugrid2=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        lt2_switch_ugrid1=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
    )


class Lt2Control(
    Control[Lt2SensorValues, Lt2ControlValues, Lt2Parameters, Lt2ControlMode]
):
    def __init__(
        self, parameters: Lt2Parameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        self._states = []

        self._transitions = []

        self._state_machine = Machine(
            model=self,
            states=self._states,
            transitions=self._transitions,
            initial="idle",
        )

        # self._heat_dump_controller = Controller[Ratio, Celsius](
        #     initial=self._current_values.lt2_mix_exchanger.setpoint.value,
        #     setpoint=lambda: self._parameters.propulsion_maximum_supply_temperature
        #     if self.mode.is_propulsion
        #     else self._parameters.shorepower_maximum_supply_temperature,
        #     tuning=lambda: self._parameters.heat_dump_tuning,
        #     time_fn=self._time,
        # )

        # self._warmup_mix_controller = Controller[Ratio, Celsius](
        #     initial=self._current_values.lt1_mix_recovery.setpoint.value,
        #     setpoint=lambda: self._parameters.recovery_temperature,
        #     tuning=lambda: self._parameters.warmup_mix_tuning,
        #     time_fn=self._time,
        # )

        # self._pump_controller_shorepower = Controller[Ratio, LMin](
        #     initial=self._current_values.lt1_pump1.dutypoint.value,
        #     setpoint=lambda: self._parameters.shorepower_flow_setpoint,
        #     tuning=lambda: self._parameters.pump_tuning,
        #     time_fn=self._time,
        # )

        # self._pump_controller_propulsion = Controller[Ratio, LMin](
        #     initial=self._current_values.lt1_pump1.dutypoint.value,
        #     setpoint=0,  # gets overriden by flow balance controller
        #     tuning=lambda: self._parameters.pump_tuning,
        #     time_fn=self._time,
        # )

    @property
    def parameters(self) -> Lt2Parameters:
        return self._parameters

    def update_parameters(self, parameters: Lt2Parameters):
        self._parameters = parameters

    def modes(self) -> list[str]:
        return list(self._state_machine.states.keys())

    @property
    def initial_mode(self) -> Lt2ControlMode:
        initial_mode: str = self._state_machine.initial  # type: ignore
        return Lt2ControlMode(mode=initial_mode)

    @property
    def mode(self) -> Lt2ControlMode:
        mode: str = self.state  # type: ignore
        return Lt2ControlMode(mode=mode)

    def initial(self) -> ControlResult[Lt2ControlValues]:
        return ControlResult(self._time(), _INITIAL_CONTROL_VALUES(self._time()))

    def control(
        self, sensor_values: Lt2SensorValues
    ) -> ControlResult[Lt2ControlValues]:
        return ControlResult(self._time(), self._current_values)


class Lt2Alarms(BaseAlarms):
    pass
