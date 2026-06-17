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
from thrs.input_output.modules.dc import DcControlValues, DcSensorValues


class DcControlMode(ControlMode):
    brightloops_aft: ConvertersControlMode
    brightloops_fwd: ConvertersControlMode
    ugrids: ConvertersControlMode


class DcParameters(ThrsValues):
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


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> DcControlValues:
    return DcControlValues(
        dc_pump_aft=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        dc_pump_fwd=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        dc_pump_ugrid=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        dc_mix_fwd=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        dc_mix_aft=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        dc_mix_ugrid=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        dc_mix_recovery=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        dc_mix_exchanger=Valve(
            setpoint=Stamped(value=Valve.MIXING_A_TO_AB, timestamp=timestamp)
        ),
        dc_switch_aft4=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        dc_switch_aft3=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        dc_switch_aft2=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        dc_switch_aft1=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        dc_switch_fwd2=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        dc_switch_fwd1=Valve(setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)),
        dc_switch_ugrid2=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
        dc_switch_ugrid1=Valve(
            setpoint=Stamped(value=Valve.CLOSED, timestamp=timestamp)
        ),
    )


def brightloops_aft_parameters(dc_parameters: DcParameters) -> ConvertersParameters:
    return ConvertersParameters(
        converter_return_temperature=dc_parameters.brightloop_return_temperature,
        converter_flow_setpoint=dc_parameters.brightloop_flow_setpoint,
        warmup_mix_tuning=dc_parameters.brightloops_aft_mix_tuning,
        pump_tuning=dc_parameters.brightloops_aft_pump_tuning,
    )


def brightloops_fwd_parameters(dc_parameters: DcParameters) -> ConvertersParameters:
    return ConvertersParameters(
        converter_return_temperature=dc_parameters.brightloop_return_temperature,
        converter_flow_setpoint=dc_parameters.brightloop_flow_setpoint,
        warmup_mix_tuning=dc_parameters.brightloops_fwd_mix_tuning,
        pump_tuning=dc_parameters.brightloops_fwd_pump_tuning,
    )


def ugrids_parameters(dc_parameters: DcParameters) -> ConvertersParameters:
    return ConvertersParameters(
        converter_return_temperature=dc_parameters.ugrid_return_temperature,
        converter_flow_setpoint=dc_parameters.ugrid_flow_setpoint,
        warmup_mix_tuning=dc_parameters.ugrids_mix_tuning,
        pump_tuning=dc_parameters.ugrids_pump_tuning,
    )


class DcControl(Control[DcSensorValues, DcControlValues, DcParameters, DcControlMode]):
    def __init__(
        self, parameters: DcParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        self._heat_dump_controller = PidController[Ratio, Celsius](
            initial=self._current_values.dc_mix_exchanger.setpoint.value,
            setpoint=lambda: self._parameters.maximum_supply_temperature,
            tuning=lambda: self._parameters.heat_dump_tuning,
            time_fn=self._time,
        )

        self._heat_dump_controller.enable()  # always enabled

        self._recovery_mix_controller = PidController[Ratio, Celsius](
            initial=self._current_values.dc_mix_recovery.setpoint.value,
            setpoint=lambda: self._parameters.recovery_temperature,
            tuning=lambda: self._parameters.recovery_mix_tuning,
            time_fn=self._time,
        )

        self._recovery_mix_controller.enable()  # always enabled

        self._brightloops_aft_control = ConvertersControl(
            brightloops_aft_parameters(parameters),
            initial_control_values=ConvertersControlValues(
                pump=self._current_values.dc_pump_aft,
                mix=self._current_values.dc_mix_aft,
                switches=[
                    self._current_values.dc_switch_aft1,
                    self._current_values.dc_switch_aft2,
                    self._current_values.dc_switch_aft3,
                    self._current_values.dc_switch_aft4,
                ],
            ),
            time_fn=self._time,
        )

        self._brightloops_fwd_control = ConvertersControl(
            brightloops_fwd_parameters(parameters),
            initial_control_values=ConvertersControlValues(
                pump=self._current_values.dc_pump_fwd,
                mix=self._current_values.dc_mix_fwd,
                switches=[
                    self._current_values.dc_switch_fwd1,
                    self._current_values.dc_switch_fwd2,
                ],
            ),
            time_fn=self._time,
        )

        self._ugrids_control = ConvertersControl(
            ugrids_parameters(parameters),
            initial_control_values=ConvertersControlValues(
                pump=self._current_values.dc_pump_ugrid,
                mix=self._current_values.dc_mix_ugrid,
                switches=[
                    self._current_values.dc_switch_ugrid1,
                    self._current_values.dc_switch_ugrid2,
                ],
            ),
            time_fn=self._time,
        )

    @property
    def parameters(self) -> DcParameters:
        return self._parameters

    def update_parameters(self, parameters: DcParameters):
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
    def initial_mode(self) -> DcControlMode:
        return DcControlMode(
            brightloops_aft=self._brightloops_aft_control.initial_mode,
            brightloops_fwd=self._brightloops_fwd_control.initial_mode,
            ugrids=self._ugrids_control.initial_mode,
        )

    @property
    def mode(self) -> DcControlMode:
        return DcControlMode(
            brightloops_aft=self._brightloops_aft_control.mode,
            brightloops_fwd=self._brightloops_fwd_control.mode,
            ugrids=self._ugrids_control.mode,
        )

    def initial(self) -> ControlResult[DcControlValues]:
        return ControlResult(self._time(), _INITIAL_CONTROL_VALUES(self._time()))

    def control(self, sensor_values: DcSensorValues) -> ControlResult[DcControlValues]:
        self._control_heat_dump(sensor_values)
        self._control_recovery_mix(sensor_values)

        self._control_groups(sensor_values)

        return ControlResult(self._time(), self._current_values)

    def _control_heat_dump(self, sensor_values: DcSensorValues):
        if self._heat_dump_controller.enabled():
            self._current_values.dc_mix_exchanger.setpoint = Stamped(
                value=self._heat_dump_controller(
                    sensor_values.dc_temperature_supply.temperature.value
                ),
                timestamp=self._time(),
            )

    def _control_recovery_mix(self, sensor_values: DcSensorValues):
        if self._recovery_mix_controller.enabled():
            self._current_values.dc_mix_recovery.setpoint = Stamped(
                value=self._recovery_mix_controller(
                    sensor_values.dc_temperature_recovery.temperature.value
                ),
                timestamp=self._time(),
            )

    def _update_group_control_values(self):
        self._current_values.dc_pump_aft = (
            self._brightloops_aft_control.current_values.pump
        )
        self._current_values.dc_pump_fwd = (
            self._brightloops_fwd_control.current_values.pump
        )
        self._current_values.dc_pump_ugrid = self._ugrids_control.current_values.pump
        self._current_values.dc_mix_aft = (
            self._brightloops_aft_control.current_values.mix
        )
        self._current_values.dc_mix_fwd = (
            self._brightloops_fwd_control.current_values.mix
        )
        self._current_values.dc_mix_ugrid = self._ugrids_control.current_values.mix
        self._current_values.dc_switch_aft1 = (
            self._brightloops_aft_control.current_values.switches[0]
        )
        self._current_values.dc_switch_aft2 = (
            self._brightloops_aft_control.current_values.switches[1]
        )
        self._current_values.dc_switch_aft3 = (
            self._brightloops_aft_control.current_values.switches[2]
        )
        self._current_values.dc_switch_aft4 = (
            self._brightloops_aft_control.current_values.switches[3]
        )
        self._current_values.dc_switch_fwd1 = (
            self._brightloops_fwd_control.current_values.switches[0]
        )
        self._current_values.dc_switch_fwd2 = (
            self._brightloops_fwd_control.current_values.switches[1]
        )
        self._current_values.dc_switch_ugrid1 = (
            self._ugrids_control.current_values.switches[0]
        )
        self._current_values.dc_switch_ugrid2 = (
            self._ugrids_control.current_values.switches[1]
        )

    def _control_groups(self, sensor_values: DcSensorValues):
        self._brightloops_aft_control.control(
            ConvertersSensorValues(
                pump=sensor_values.dc_pump_aft,
                temperature_supply=sensor_values.dc_temperature_aft_supply,
                temperature_return=sensor_values.dc_temperature_aft_return,
                pressure=sensor_values.dc_pressure_aft,
                mix=sensor_values.dc_mix_aft,
                flows=[
                    sensor_values.dc_flow_aft1,
                    sensor_values.dc_flow_aft2,
                    sensor_values.dc_flow_aft3,
                    sensor_values.dc_flow_aft4,
                ],
                switches=[
                    sensor_values.dc_switch_aft1,
                    sensor_values.dc_switch_aft2,
                    sensor_values.dc_switch_aft3,
                    sensor_values.dc_switch_aft4,
                ],
                converters=[
                    sensor_values.dc_brightloop_aft1,
                    sensor_values.dc_brightloop_aft2,
                    sensor_values.dc_brightloop_aft3,
                    sensor_values.dc_brightloop_aft4,
                ],
                converter_return_temperatures=[
                    sensor_values.dc_temperature_aft1_return,
                    sensor_values.dc_temperature_aft2_return,
                    sensor_values.dc_temperature_aft3_return,
                    sensor_values.dc_temperature_aft4_return,
                ],
            )
        )

        self._brightloops_fwd_control.control(
            ConvertersSensorValues(
                pump=sensor_values.dc_pump_fwd,
                temperature_supply=sensor_values.dc_temperature_fwd_supply,
                temperature_return=sensor_values.dc_temperature_fwd_return,
                pressure=sensor_values.dc_pressure_fwd,
                mix=sensor_values.dc_mix_fwd,
                flows=[sensor_values.dc_flow_fwd1, sensor_values.dc_flow_fwd2],
                switches=[sensor_values.dc_switch_fwd1, sensor_values.dc_switch_fwd2],
                converters=[
                    sensor_values.dc_brightloop_fwd1,
                    sensor_values.dc_brightloop_fwd2,
                ],
                converter_return_temperatures=[
                    sensor_values.dc_temperature_fwd1_return,
                    sensor_values.dc_temperature_fwd2_return,
                ],
            )
        )

        self._ugrids_control.control(
            ConvertersSensorValues(
                pump=sensor_values.dc_pump_ugrid,
                temperature_supply=sensor_values.dc_temperature_ugrid_supply,
                temperature_return=sensor_values.dc_temperature_ugrid_return,
                pressure=sensor_values.dc_pressure_ugrid,
                mix=sensor_values.dc_mix_ugrid,
                flows=[sensor_values.dc_flow_ugrid1, sensor_values.dc_flow_ugrid2],
                switches=[
                    sensor_values.dc_switch_ugrid1,
                    sensor_values.dc_switch_ugrid2,
                ],
                converters=[sensor_values.dc_ugrid1, sensor_values.dc_ugrid2],
                converter_return_temperatures=[
                    sensor_values.dc_temperature_ugrid1_return,
                    sensor_values.dc_temperature_ugrid2_return,
                ],
            )
        )

        self._update_group_control_values()


class DcAlarms(BaseAlarms):
    pass


LT2_MODULE_DESCRIPTION = ModuleDescription(
    DcSensorValues,
    DcControlValues,
    DcParameters,
    DcControl,
    DcControlMode,
    DcAlarms,
)
