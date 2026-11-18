from typing import Annotated

from pydantic import model_validator

from thrs.classes.control import ControlMode
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import Celsius, Tuning


class AdsorptionControlMode(ControlMode):
    mode: str


class AdsorptionParameters(ThrsValues):
    chiller_enabled: bool = True
    waste_cooling_temperature_setpoint: Celsius = 35.0
    waste_recovery_temperature_setpoint: Celsius = 34.0
    hot_supply_temperature_setpoint: Celsius = 60.0
    adsorption_cooling_setpoint: Celsius = 17.0
    adsorption_hot_minimum: Celsius = 50.0
    adsorption_hot_trigger: Celsius = 55.0
    adsorption_cold_minimum: Celsius = 10.0
    adsorption_cold_trigger: Celsius = 17.0
    hot_mix_tuning: Tuning = (0.05, 0.001, 0)
    recovery_tuning: Tuning = (0.05, 0.001, 0)
    waste_cooling_tuning: Tuning = (0.05, 0.01, 0)
    free_cooling_enabled: bool = False

    @model_validator(mode="after")
    def check_temperature_setpoints(self):
        if self.adsorption_hot_trigger <= self.adsorption_hot_minimum:
            raise ValueError(
                "Hot trigger temperature must be greater than hot minimum temperature"
            )
        if self.adsorption_cold_trigger <= self.adsorption_cold_minimum:
            raise ValueError(
                "Cold trigger temperature must be greater than cold minimum temperature"
            )
        return self


class AdsorptionControllerState(ThrsValues):
    adsorption_hot_mix_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    adsorption_recovery_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    adsorption_waste_cooling_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
