from typing import Annotated

from pydantic import Field, model_validator

from thrs.classes.control import ControlMode
from thrs.control.modules.dhw.io import DhwControlValues
from thrs.control.state import ControlState
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.controllers import (
    PidControllerValues,
    TanksControllerValues,
)
from thrs.input_output.definitions.units import (
    Celsius,
    DeltaT,
    Liter,
    LMin,
    Ratio,
    Seconds,
    Tuning,
    Watt,
)


class DhwControlMode(ControlMode):
    boosting_mode: str
    filling_mode: str

    @property
    def is_boosting_idle(self) -> bool:
        return self.boosting_mode == "idle"

    @property
    def is_boosting(self) -> bool:
        return not self.is_boosting_idle

    @property
    def is_boosting_low_temperature(self) -> bool:
        return self.boosting_mode == "boosting_low_temperature"

    @property
    def is_boosting_high_temperature(self) -> bool:
        return self.boosting_mode == "boosting_high_temperature"

    @property
    def is_boosting_heatpump(self) -> bool:
        return self.boosting_mode == "boosting_heatpump"


class DhwParameters(ThrsValues):
    heatpump_boosting_enabled: bool = False
    ht_boosting_enabled: bool = True
    heatpump_flow_setpoint: LMin = 25
    heatpump_temperature_setpoint: Celsius = 65
    ht_boosting_flow_setpoint: LMin = 10
    minimum_tank_temperature: Celsius = 45
    maximum_tank_temperature: Celsius = 60
    ht_boosting_minimum_delta: Annotated[
        DeltaT,
        Field(
            description="Minimum delta T between the HT boosting source and the tank to start or continue HT boosting"
        ),
    ] = 3
    boosting_startup_grace: Annotated[
        Seconds,
        Field(
            description="Grace period after boosting starts on a source or tank before the stall guard checks heat transfer, covering valve travel, pump ramp and heatpump spin-up",
            ge=0,
        ),
    ] = 180
    boosting_stall_window: Annotated[
        Seconds,
        Field(
            description="How long boosting heat transfer must stay below boosting_minimum_heat before the tank counts as stalled",
            ge=0,
        ),
    ] = 120
    boosting_stall_lockout: Annotated[
        Seconds,
        Field(
            description="Lockout before a boosting source boosts a tank again after it stalled on that tank",
            ge=0,
        ),
    ] = 900
    boosting_minimum_heat: Annotated[
        Watt,
        Field(
            description="Minimum heat transfer to the tank in Watt (~1 kW) below which boosting is considered stalled",
            ge=0,
        ),
    ] = 1000
    drives_flowcontrol_minimum_setpoint: Annotated[
        Ratio,
        Field(
            description="Minimum pump dutypoint to guarantee sufficient flow for a temperature measurement"
        ),
    ] = 0.1
    dc_flowcontrol_minimum_setpoint: Annotated[
        Ratio,
        Field(
            description="Minimum pump dutypoint to guarantee sufficient flow for a temperature measurement"
        ),
    ] = 0.1
    minimum_pump_dutypoint: Annotated[
        Ratio,
        Field(
            description="Minimum output of the boosting pump controllers",
            ge=0.1,
            le=1.0,
        ),
    ] = 0.3
    filling_temperature_setpoint: Celsius = 40
    minimum_tank_level: Liter = 30
    maximum_tank_level: Annotated[Liter, Field(le=275)] = 230
    full_level_lower_band: Annotated[
        Liter, Field(description="Level above which a non-filling tank counts as full")
    ] = 200
    tank1_enabled: bool = True
    tank2_enabled: bool = True
    tank3_enabled: bool = True
    pump_flow_tuning: Tuning = (0.01, 0.001, 0.0)
    dc_flow_tuning: Tuning = (-0.01, -0.001, 0.0)
    drives_flow_tuning: Tuning = (-0.01, -0.001, 0.0)

    @model_validator(mode="after")
    def check_tank_setpoints(self):
        if self.minimum_tank_temperature > self.maximum_tank_temperature:
            raise ValueError(
                "Maximum tank temperature must be greater than minimum tank temperature"
            )
        if self.minimum_tank_level > self.maximum_tank_level:
            raise ValueError(
                "Maximum tank level must be greater than minimum tank level"
            )
        if self.full_level_lower_band > self.maximum_tank_level:
            raise ValueError("Full level lower band must not exceed maximum tank level")
        if self.minimum_tank_level > self.full_level_lower_band:
            raise ValueError(
                "Full level lower band must not be below minimum tank level"
            )
        return self


class DhwControllerState(ControlState[DhwControlValues, DhwParameters, DhwControlMode]):
    dhw_tanks_controller: Annotated[
        TanksControllerValues,
        component_meta(component_type="tank_controller"),
    ]
    dhw_pump_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dhw_drives_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    dhw_dc_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
