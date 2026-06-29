from datetime import datetime
from typing import Annotated, Callable

from pydantic import Field, model_validator

from thrs.classes.control import Control, ControlMode
from thrs.control.controllers import PidController
from thrs.control.modules.pvt_group import (
    PvtGroupControl,
    PvtGroupControlMode,
    PvtGroupControlValues,
    PvtGroupParameters,
    PvtGroupSensorValues,
)
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import Celsius, Ratio, Tuning
from thrs.input_output.modules.pvt import PvtControlValues, PvtSensorValues
from thrs.orchestration.module import ModuleDescription


class PvtControlMode(ControlMode):
    aft: PvtGroupControlMode
    fwd: PvtGroupControlMode
    owners: PvtGroupControlMode


class PvtParameters(ThrsValues):
    maximum_supply_temperature: Annotated[Celsius, Field(le=90)] = 80
    recovery_temperature: Celsius = 70
    warmup_temperature: Celsius = 55
    recovery_activation_string_temperature: Celsius = 40
    minimum_return_temperature: Celsius = 40
    main_fwd_minimum_pump_dutypoint: Ratio = 0.3  # minimum dutpypoint to ensure flow past temperature sensor in recovery mode (~10l/min)
    main_aft_minimum_pump_dutypoint: Ratio = 0.3  # minimum dutpypoint to ensure flow past temperature sensor in recovery mode (~10l/min)
    owners_minimum_pump_dutypoint: Ratio = 0.4  # minimum dutpypoint to ensure flow past temperature sensor in recovery mode (~10l/min)
    heat_dump_tuning: Tuning = (0.05, 0.001, 0.0)
    main_fwd_mix_tuning: Tuning = (-0.005, -0.001, 0.0)
    main_aft_mix_tuning: Tuning = (-0.005, -0.001, 0.0)
    owners_mix_tuning: Tuning = (-0.005, -0.001, 0.0)
    main_fwd_pump_tuning: Tuning = (
        -0.0005,
        -0.0001,
        -0.00001,
    )
    main_aft_pump_tuning: Tuning = (
        -0.0005,
        -0.0001,
        -0.00001,
    )
    owners_pump_tuning: Tuning = (
        -0.0005,
        -0.0001,
        -0.00001,
    )

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


def _INITIAL_CONTROL_VALUES(timestamp: datetime) -> PvtControlValues:
    return PvtControlValues(
        pvt_pump_main_fwd=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        pvt_pump_main_aft=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        pvt_pump_owners=Pump(
            dutypoint=Stamped(value=0.0, timestamp=timestamp),
            on=Stamped(value=False, timestamp=timestamp),
        ),
        pvt_mix_main_fwd=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        pvt_mix_main_aft=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        pvt_mix_owners=Valve(
            setpoint=Stamped(value=Valve.MIXING_B_TO_AB, timestamp=timestamp)
        ),
        pvt_switch_main_fwd=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        pvt_switch_main_aft=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        pvt_switch_owners=Valve(
            setpoint=Stamped(value=Valve.OPEN, timestamp=timestamp)
        ),
        pvt_mix_exchanger=Valve(
            setpoint=Stamped(
                value=Valve.MIXING_A_TO_AB,
                timestamp=timestamp,
            )
        ),
    )


def main_pvt_group_parameters(pvt_parameters: PvtParameters) -> PvtGroupParameters:
    return PvtGroupParameters(
        warmup_temperature=pvt_parameters.warmup_temperature,
        recovery_temperature=pvt_parameters.recovery_temperature,
        warmup_mix_tuning=pvt_parameters.main_fwd_mix_tuning,
        pump_tuning=pvt_parameters.main_fwd_pump_tuning,
        minimum_pump_dutypoint=pvt_parameters.main_fwd_minimum_pump_dutypoint,
        recovery_activation_string_temperature=pvt_parameters.recovery_activation_string_temperature,
        minimum_return_temperature=pvt_parameters.minimum_return_temperature,
    )


def aft_pvt_group_parameters(pvt_parameters: PvtParameters) -> PvtGroupParameters:
    return PvtGroupParameters(
        warmup_temperature=pvt_parameters.warmup_temperature,
        recovery_temperature=pvt_parameters.recovery_temperature,
        warmup_mix_tuning=pvt_parameters.main_aft_mix_tuning,
        pump_tuning=pvt_parameters.main_aft_pump_tuning,
        minimum_pump_dutypoint=pvt_parameters.main_aft_minimum_pump_dutypoint,
        recovery_activation_string_temperature=pvt_parameters.recovery_activation_string_temperature,
        minimum_return_temperature=pvt_parameters.minimum_return_temperature,
    )


def owners_pvt_group_parameters(pvt_parameters: PvtParameters) -> PvtGroupParameters:
    return PvtGroupParameters(
        warmup_temperature=pvt_parameters.warmup_temperature,
        recovery_temperature=pvt_parameters.recovery_temperature,
        warmup_mix_tuning=pvt_parameters.owners_mix_tuning,
        pump_tuning=pvt_parameters.owners_pump_tuning,
        minimum_pump_dutypoint=pvt_parameters.owners_minimum_pump_dutypoint,
        recovery_activation_string_temperature=pvt_parameters.recovery_activation_string_temperature,
        minimum_return_temperature=pvt_parameters.minimum_return_temperature,
    )


class PvtControl(
    Control[PvtSensorValues, PvtControlValues, PvtParameters, PvtControlMode]
):
    def __init__(
        self, parameters: PvtParameters, time_fn: Callable[[], datetime]
    ) -> None:
        self._parameters = parameters
        self._time = time_fn
        self._current_values = _INITIAL_CONTROL_VALUES(self._time()).model_copy(
            deep=True
        )

        self._heat_dump_controller = PidController[Ratio, Celsius](
            self._current_values.pvt_mix_exchanger.setpoint.value,
            lambda: self._parameters.maximum_supply_temperature,
            lambda: self._parameters.heat_dump_tuning,
            self._time,
        )

        self._heat_dump_controller.enable()  # always enabled

        self._main_fwd_control = PvtGroupControl(
            main_pvt_group_parameters(parameters),
            initial_control_values=PvtGroupControlValues(
                pump=self._current_values.pvt_pump_main_fwd,
                mix=self._current_values.pvt_mix_main_fwd,
            ),
            time_fn=time_fn,
        )
        self._main_aft_control = PvtGroupControl(
            aft_pvt_group_parameters(parameters),
            initial_control_values=PvtGroupControlValues(
                pump=self._current_values.pvt_pump_main_aft,
                mix=self._current_values.pvt_mix_main_aft,
            ),
            time_fn=time_fn,
        )
        self._owners_control = PvtGroupControl(
            owners_pvt_group_parameters(parameters),
            initial_control_values=PvtGroupControlValues(
                pump=self._current_values.pvt_pump_owners,
                mix=self._current_values.pvt_mix_owners,
            ),
            time_fn=time_fn,
        )

    @property
    def parameters(self) -> PvtParameters:
        return self._parameters

    @property
    def mode(self) -> PvtControlMode:
        return PvtControlMode(
            fwd=self._main_fwd_control.mode,
            aft=self._main_aft_control.mode,
            owners=self._owners_control.mode,
        )

    @staticmethod
    def modes() -> list[str]:
        return [""]

    @property
    def initial_mode(self) -> PvtControlMode:
        return PvtControlMode(
            fwd=self._main_fwd_control.initial_mode,
            aft=self._main_aft_control.initial_mode,
            owners=self._owners_control.initial_mode,
        )

    def initial(self) -> PvtControlValues:
        return _INITIAL_CONTROL_VALUES(self._time())

    def update_parameters(self, parameters: PvtParameters):
        self._parameters = parameters
        self._main_fwd_control.update_parameters(main_pvt_group_parameters(parameters))
        self._main_aft_control.update_parameters(aft_pvt_group_parameters(parameters))
        self._owners_control.update_parameters(owners_pvt_group_parameters(parameters))

    def _control_heat_dump(self, sensor_values: PvtSensorValues):
        self._current_values.pvt_mix_exchanger.setpoint = Stamped(
            value=self._heat_dump_controller(
                sensor_values.pvt_temperature_supply.temperature.value
            ),
            timestamp=self._time(),
        )

    def _update_group_control_values(self):
        self._current_values.pvt_pump_main_fwd = (
            self._main_fwd_control.current_values.pump
        )
        self._current_values.pvt_mix_main_fwd = (
            self._main_fwd_control.current_values.mix
        )

        self._current_values.pvt_pump_main_aft = (
            self._main_aft_control.current_values.pump
        )
        self._current_values.pvt_mix_main_aft = (
            self._main_aft_control.current_values.mix
        )

        self._current_values.pvt_pump_owners = self._owners_control.current_values.pump
        self._current_values.pvt_mix_owners = self._owners_control.current_values.mix

    def _control_groups(self, sensor_values: PvtSensorValues):
        self._main_fwd_control.control(
            PvtGroupSensorValues(
                pump=sensor_values.pvt_pump_main_fwd,
                temperature_supply=sensor_values.pvt_temperature_main_fwd_supply,
                temperature_return=sensor_values.pvt_temperature_main_fwd_return,
                pressure=sensor_values.pvt_pressure_main_fwd,
                mix=sensor_values.pvt_mix_main_fwd,
                max_temperature_strings=sensor_values.pvt_max_temperature_main_fwd_strings,
            )
        )
        self._main_aft_control.control(
            PvtGroupSensorValues(
                pump=sensor_values.pvt_pump_main_aft,
                temperature_supply=sensor_values.pvt_temperature_main_aft_supply,
                temperature_return=sensor_values.pvt_temperature_main_aft_return,
                pressure=sensor_values.pvt_pressure_main_aft,
                mix=sensor_values.pvt_mix_main_aft,
                max_temperature_strings=sensor_values.pvt_max_temperature_main_aft_strings,
            )
        )
        self._owners_control.control(
            PvtGroupSensorValues(
                pump=sensor_values.pvt_pump_owners,
                temperature_supply=sensor_values.pvt_temperature_owners_supply,
                temperature_return=sensor_values.pvt_temperature_owners_return,
                pressure=sensor_values.pvt_pressure_owners,
                mix=sensor_values.pvt_mix_owners,
                max_temperature_strings=sensor_values.pvt_max_temperature_owners_strings,
            )
        )

        self._update_group_control_values()

    def control(self, sensor_values: PvtSensorValues) -> PvtControlValues:
        self._control_heat_dump(sensor_values)

        self._control_groups(sensor_values)

        return self._current_values


class PvtAlarms(BaseAlarms):
    pass


PVT_MODULE_DESCRIPTION = ModuleDescription(
    PvtSensorValues,
    PvtControlValues,
    PvtParameters,
    PvtControl,
    PvtControlMode,
    PvtAlarms,
)
