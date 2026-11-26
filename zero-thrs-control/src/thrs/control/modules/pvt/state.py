from typing import Annotated

from pydantic import Field, model_validator

from thrs.control.modules.pvt.group import PvtGroupControlMode
from thrs.control.modules.pvt.io import PvtControlValues
from thrs.control.state import ControlMode, ControlState
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import Celsius, Ratio, Tuning


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


class PvtControllerState(ControlState[PvtControlValues, PvtParameters, PvtControlMode]):
    pvt_heat_dump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pvt_main_aft_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pvt_main_aft_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pvt_main_fwd_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pvt_main_fwd_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pvt_owners_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pvt_owners_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
