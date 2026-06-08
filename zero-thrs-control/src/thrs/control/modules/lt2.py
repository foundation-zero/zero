from datetime import datetime
from typing import Callable

from thrs.classes.control import Control, ControlMode, ControlResult
from thrs.control.base import ModuleDescription
from thrs.control.controllers import PidController
from thrs.control.modules.converters import (
    ConvertersControl,
    ConvertersControlMode,
    ConvertersControlValues,
    ConvertersParameters,
    ConvertersSensorValues,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, LMin, Ratio, Tuning
from thrs.input_output.modules.lt2 import Lt2ControlValues, Lt2SensorValues


class Lt2ControlMode(ControlMode):
    brightloops_aft: ConvertersControlMode
    brightloops_fwd: ConvertersControlMode
    ugrids: ConvertersControlMode


class Lt2Parameters(ThrsValues):
    maximum_supply_temperature: Celsius = 63
    recovery_temperature: Celsius = 60
    brightloop_flow_setpoint: LMin = 5
    ugrid_flow_setpoint: LMin = 15
    brightloop_return_temperature: Celsius = 60
    ugrid_return_temperature: Celsius = 60
    heat_dump_tuning: Tuning = (0.01, 0.001, 0.001)
    recovery_mix_tuning: Tuning = (-0.01, -0.001, -0.01)
    brightloops_fwd_mix_tuning: Tuning = (-0.01, -0.001, -0.01)
    brightloops_aft_mix_tuning: Tuning = (-0.01, -0.001, -0.01)
    ugrids_mix_tuning: Tuning = (-0.01, -0.001, -0.01)
    brightloops_fwd_pump_tuning: Tuning = (0.01, 0.001, 0)
    brightloops_aft_pump_tuning: Tuning = (0.01, 0.001, 0)
    ugrids_pump_tuning: Tuning = (0.01, 0.001, 0)


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


def brightloops_aft_parameters(lt2_parameters: Lt2Parameters) -> ConvertersParameters:
    return ConvertersParameters(
        converter_return_temperature=lt2_parameters.brightloop_return_temperature,
        converter_flow_setpoint=lt2_parameters.brightloop_flow_setpoint,
        warmup_mix_tuning=lt2_parameters.brightloops_aft_mix_tuning,
        pump_tuning=lt2_parameters.brightloops_aft_pump_tuning,
    )


def brightloops_fwd_parameters(lt2_parameters: Lt2Parameters) -> ConvertersParameters:
    return ConvertersParameters(
        converter_return_temperature=lt2_parameters.brightloop_return_temperature,
        converter_flow_setpoint=lt2_parameters.brightloop_flow_setpoint,
        warmup_mix_tuning=lt2_parameters.brightloops_fwd_mix_tuning,
        pump_tuning=lt2_parameters.brightloops_fwd_pump_tuning,
    )


def ugrids_parameters(lt2_parameters: Lt2Parameters) -> ConvertersParameters:
    return ConvertersParameters(
        converter_return_temperature=lt2_parameters.ugrid_return_temperature,
        converter_flow_setpoint=lt2_parameters.ugrid_flow_setpoint,
        warmup_mix_tuning=lt2_parameters.ugrids_mix_tuning,
        pump_tuning=lt2_parameters.ugrids_pump_tuning,
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

        self._heat_dump_controller = PidController[Ratio, Celsius](
            initial=self._current_values.lt2_mix_exchanger.setpoint.value,
            setpoint=lambda: self._parameters.maximum_supply_temperature,
            tuning=lambda: self._parameters.heat_dump_tuning,
            time_fn=self._time,
        )

        self._heat_dump_controller.enable()  # always enabled

        self._recovery_mix_controller = PidController[Ratio, Celsius](
            initial=self._current_values.lt2_mix_recovery.setpoint.value,
            setpoint=lambda: self._parameters.recovery_temperature,
            tuning=lambda: self._parameters.recovery_mix_tuning,
            time_fn=self._time,
        )

        self._recovery_mix_controller.enable()  # always enabled

        self._brightloops_aft_control = ConvertersControl(
            brightloops_aft_parameters(parameters),
            initial_control_values=ConvertersControlValues(
                pump=self._current_values.lt2_pump_aft,
                mix=self._current_values.lt2_mix_aft,
                switches=[
                    self._current_values.lt2_switch_aft1,
                    self._current_values.lt2_switch_aft2,
                    self._current_values.lt2_switch_aft3,
                    self._current_values.lt2_switch_aft4,
                ],
            ),
            time_fn=self._time,
        )

        self._brightloops_fwd_control = ConvertersControl(
            brightloops_fwd_parameters(parameters),
            initial_control_values=ConvertersControlValues(
                pump=self._current_values.lt2_pump_fwd,
                mix=self._current_values.lt2_mix_fwd,
                switches=[
                    self._current_values.lt2_switch_fwd1,
                    self._current_values.lt2_switch_fwd2,
                ],
            ),
            time_fn=self._time,
        )

        self._ugrids_control = ConvertersControl(
            ugrids_parameters(parameters),
            initial_control_values=ConvertersControlValues(
                pump=self._current_values.lt2_pump_ugrid,
                mix=self._current_values.lt2_mix_ugrid,
                switches=[
                    self._current_values.lt2_switch_ugrid1,
                    self._current_values.lt2_switch_ugrid2,
                ],
            ),
            time_fn=self._time,
        )

    @property
    def parameters(self) -> Lt2Parameters:
        return self._parameters

    def update_parameters(self, parameters: Lt2Parameters):
        self._parameters = parameters
        self._brightloops_aft_control.update_parameters(
            brightloops_aft_parameters(parameters)
        )
        self._brightloops_fwd_control.update_parameters(
            brightloops_fwd_parameters(parameters)
        )
        self._ugrids_control.update_parameters(ugrids_parameters(parameters))

    @staticmethod
    def modes() -> list[str]:
        return [""]

    @property
    def initial_mode(self) -> Lt2ControlMode:
        return Lt2ControlMode(
            brightloops_aft=self._brightloops_aft_control.initial_mode,
            brightloops_fwd=self._brightloops_fwd_control.initial_mode,
            ugrids=self._ugrids_control.initial_mode,
        )

    @property
    def mode(self) -> Lt2ControlMode:
        return Lt2ControlMode(
            brightloops_aft=self._brightloops_aft_control.mode,
            brightloops_fwd=self._brightloops_fwd_control.mode,
            ugrids=self._ugrids_control.mode,
        )

    def initial(self) -> ControlResult[Lt2ControlValues]:
        return ControlResult(self._time(), _INITIAL_CONTROL_VALUES(self._time()))

    def control(
        self, sensor_values: Lt2SensorValues
    ) -> ControlResult[Lt2ControlValues]:
        self._control_heat_dump(sensor_values)
        self._control_recovery_mix(sensor_values)

        self._control_groups(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _control_heat_dump(self, sensor_values: Lt2SensorValues):
        if self._heat_dump_controller.enabled():
            self._current_values.lt2_mix_exchanger.setpoint = Stamped(
                value=self._heat_dump_controller(
                    sensor_values.lt2_temperature_supply.temperature.value
                ),
                timestamp=self._time(),
            )

    def _control_recovery_mix(self, sensor_values: Lt2SensorValues):
        if self._recovery_mix_controller.enabled():
            self._current_values.lt2_mix_recovery.setpoint = Stamped(
                value=self._recovery_mix_controller(
                    sensor_values.lt2_temperature_recovery.temperature.value
                ),
                timestamp=self._time(),
            )

    def _update_group_control_values(self):
        self._current_values.lt2_pump_aft = (
            self._brightloops_aft_control.current_values.pump
        )
        self._current_values.lt2_pump_fwd = (
            self._brightloops_fwd_control.current_values.pump
        )
        self._current_values.lt2_pump_ugrid = self._ugrids_control.current_values.pump
        self._current_values.lt2_mix_aft = (
            self._brightloops_aft_control.current_values.mix
        )
        self._current_values.lt2_mix_fwd = (
            self._brightloops_fwd_control.current_values.mix
        )
        self._current_values.lt2_mix_ugrid = self._ugrids_control.current_values.mix
        self._current_values.lt2_switch_aft1 = (
            self._brightloops_aft_control.current_values.switches[0]
        )
        self._current_values.lt2_switch_aft2 = (
            self._brightloops_aft_control.current_values.switches[1]
        )
        self._current_values.lt2_switch_aft3 = (
            self._brightloops_aft_control.current_values.switches[2]
        )
        self._current_values.lt2_switch_aft4 = (
            self._brightloops_aft_control.current_values.switches[3]
        )
        self._current_values.lt2_switch_fwd1 = (
            self._brightloops_fwd_control.current_values.switches[0]
        )
        self._current_values.lt2_switch_fwd2 = (
            self._brightloops_fwd_control.current_values.switches[1]
        )
        self._current_values.lt2_switch_ugrid1 = (
            self._ugrids_control.current_values.switches[0]
        )
        self._current_values.lt2_switch_ugrid2 = (
            self._ugrids_control.current_values.switches[1]
        )

    def _control_groups(self, sensor_values: Lt2SensorValues):
        self._brightloops_aft_control.control(
            ConvertersSensorValues(
                pump=sensor_values.lt2_pump_aft,
                temperature_supply=sensor_values.lt2_temperature_aft_supply,
                temperature_return=sensor_values.lt2_temperature_aft_return,
                pressure=sensor_values.lt2_pressure_aft,
                mix=sensor_values.lt2_mix_aft,
                flows=[
                    sensor_values.lt2_flow_aft1,
                    sensor_values.lt2_flow_aft2,
                    sensor_values.lt2_flow_aft3,
                    sensor_values.lt2_flow_aft4,
                ],
                switches=[
                    sensor_values.lt2_switch_aft1,
                    sensor_values.lt2_switch_aft2,
                    sensor_values.lt2_switch_aft3,
                    sensor_values.lt2_switch_aft4,
                ],
                converters=[
                    sensor_values.lt2_brightloop_aft1,
                    sensor_values.lt2_brightloop_aft2,
                    sensor_values.lt2_brightloop_aft3,
                    sensor_values.lt2_brightloop_aft4,
                ],
                converter_return_temperatures=[
                    sensor_values.lt2_temperature_aft1_return,
                    sensor_values.lt2_temperature_aft2_return,
                    sensor_values.lt2_temperature_aft3_return,
                    sensor_values.lt2_temperature_aft4_return,
                ],
            )
        )

        self._brightloops_fwd_control.control(
            ConvertersSensorValues(
                pump=sensor_values.lt2_pump_fwd,
                temperature_supply=sensor_values.lt2_temperature_fwd_supply,
                temperature_return=sensor_values.lt2_temperature_fwd_return,
                pressure=sensor_values.lt2_pressure_fwd,
                mix=sensor_values.lt2_mix_fwd,
                flows=[sensor_values.lt2_flow_fwd1, sensor_values.lt2_flow_fwd2],
                switches=[sensor_values.lt2_switch_fwd1, sensor_values.lt2_switch_fwd2],
                converters=[
                    sensor_values.lt2_brightloop_fwd1,
                    sensor_values.lt2_brightloop_fwd2,
                ],
                converter_return_temperatures=[
                    sensor_values.lt2_temperature_fwd1_return,
                    sensor_values.lt2_temperature_fwd2_return,
                ],
            )
        )

        self._ugrids_control.control(
            ConvertersSensorValues(
                pump=sensor_values.lt2_pump_ugrid,
                temperature_supply=sensor_values.lt2_temperature_ugrid_supply,
                temperature_return=sensor_values.lt2_temperature_ugrid_return,
                pressure=sensor_values.lt2_pressure_ugrid,
                mix=sensor_values.lt2_mix_ugrid,
                flows=[sensor_values.lt2_flow_ugrid1, sensor_values.lt2_flow_ugrid2],
                switches=[
                    sensor_values.lt2_switch_ugrid1,
                    sensor_values.lt2_switch_ugrid2,
                ],
                converters=[sensor_values.lt2_ugrid1, sensor_values.lt2_ugrid2],
                converter_return_temperatures=[
                    sensor_values.lt2_temperature_ugrid1_return,
                    sensor_values.lt2_temperature_ugrid2_return,
                ],
            )
        )

        self._update_group_control_values()


class Lt2Alarms(BaseAlarms):
    pass


LT2_MODULE_DESCRIPTION = ModuleDescription(
    Lt2SensorValues,
    Lt2ControlValues,
    Lt2Parameters,
    Lt2Control,
    Lt2ControlMode,
    Lt2Alarms,
)
