from typing import Annotated

from pydantic import Field, model_validator

from thrs.classes.control import ControlMode
from thrs.control.controllers import PcmChargeController
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.controllers import (
    PcmChargeControllerValues,
    PidControllerValues,
)
from thrs.input_output.definitions.units import Celsius, LMin, Seconds, Tuning


class PcmControlMode(ControlMode):
    mode: str

    @property
    def is_idle(self) -> bool:
        return self.mode == "idle"

    @property
    def is_supplying(self) -> bool:
        return self.mode == "supplying"

    @property
    def is_charging(self) -> bool:
        return self.mode == "charging"

    @property
    def is_boosting(self) -> bool:
        return self.mode == "boosting"


class PcmParameters(ThrsValues):
    pcm_discharge_flow: LMin = 5
    pcm_charge_flow: LMin = 5
    minimum_charging_temperature: Annotated[
        Celsius,
        Field(description="Range for thermal charging", ge=65, le=80),
    ] = 65
    pump_tuning: Tuning = (0.01, 0.001, 0)
    charging_requested: Annotated[
        bool,
        Field(description="Keep trying to charge the PCM modules while possible"),
    ] = False
    supplying_requested: Annotated[
        bool,
        Field(
            description="Keep trying to supply heat from the PCM modules while possible"
        ),
    ] = False
    grace_period: Annotated[
        Seconds,
        Field(
            description="Grace period after entering charging/supplying before the stall guard checks a module's charging_state",
            ge=0,
        ),
    ] = 120
    stall_duration: Annotated[
        Seconds,
        Field(
            description="How long a module's charging_state may fail to show it actually (dis)charging before it is dropped as stalled",
            ge=0,
        ),
    ] = 120
    retry_delay: Annotated[
        Seconds,
        Field(
            description="Lockout before retrying a mode after all its modules stalled and were dropped",
            ge=0,
        ),
    ] = 600
    module1_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module2_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module3_flow_balance_tuning: Tuning = (0.05, 0.01, 0)
    module4_flow_balance_tuning: Tuning = (0.05, 0.01, 0)

    @model_validator(mode="after")
    def check_not_both_requested(self):
        if self.charging_requested and self.supplying_requested:
            raise ValueError("Charging and supplying cannot both be requested")
        return self

    @model_validator(mode="after")
    def check_charging_can_anchor_full(self):
        if self.pcm_charge_flow <= 0:
            raise ValueError("PCM charge flow must be greater than zero")
        bound = PcmChargeController.minimum_charging_temperature(self.pcm_charge_flow)
        if self.minimum_charging_temperature <= bound:
            raise ValueError(
                f"Minimum charging temperature must be above {bound:.1f} C at a "
                f"charge flow of {self.pcm_charge_flow} l/min"
            )
        return self


class PcmControllerState(ThrsValues):
    pcm_pump_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pcm_module1_charge_controller: Annotated[
        PcmChargeControllerValues,
        component_meta(component_type="pcm_charge_controller"),
    ]
    pcm_module2_charge_controller: Annotated[
        PcmChargeControllerValues,
        component_meta(component_type="pcm_charge_controller"),
    ]
    pcm_module3_charge_controller: Annotated[
        PcmChargeControllerValues,
        component_meta(component_type="pcm_charge_controller"),
    ]
    pcm_module4_charge_controller: Annotated[
        PcmChargeControllerValues,
        component_meta(component_type="pcm_charge_controller"),
    ]
    pcm_module1_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pcm_module2_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pcm_module3_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    pcm_module4_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
