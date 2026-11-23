from typing import Annotated

from pydantic import model_validator

from thrs.classes.control import ControlMode
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import Celsius, LMin, Tuning


class ThrustersControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"

    @property
    def is_warmup(self) -> bool:
        return self.mode == "warmup"

    @property
    def is_recovery(self) -> bool:
        return self.mode == "recovery"


class ThrustersParameters(ThrsValues):
    maximum_supply_temperature: Celsius = 75
    cooling_temperature: Celsius = 38
    cooling_flow: LMin = 25
    recovery_temperature: Celsius = 65
    warmup_temperature: Celsius = 60
    thrusters_minimum_flow: LMin = 5
    thrusters_maximum_flow: LMin = 30
    pump_tuning: Tuning = (0.01, 0.001, 0)
    warmup_mix_tuning: Tuning = (-0.05, -0.001, 0)
    heat_dump_tuning: Tuning = (0.05, 0.01, 0)
    aft_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    fwd_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    aft_temperature_tuning: Tuning = (-0.01, -0.001, 0)
    fwd_temperature_tuning: Tuning = (-0.01, -0.001, 0)

    @model_validator(mode="after")
    def check_temperature_setpoints(self):
        if self.maximum_supply_temperature < self.recovery_temperature:
            raise ValueError(
                "Maximum recovery temperature must be greater than recovery temperature"
            )
        if self.recovery_temperature < self.warmup_temperature:
            raise ValueError(
                "Recovery temperature must be greater than warmup temperature"
            )
        if self.warmup_temperature < self.cooling_temperature:
            raise ValueError(
                "Warmup temperature must be greater than cooling temperature"
            )
        return self


class ThrustersControllerState(ThrsValues):
    thrusters_heat_dump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    thrusters_warmup_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    thrusters_pump_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    thrusters_aft_recovery_temperature_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    thrusters_fwd_recovery_temperature_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    thrusters_aft_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    thrusters_fwd_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
