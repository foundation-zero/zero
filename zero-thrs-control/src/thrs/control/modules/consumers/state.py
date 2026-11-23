from typing import Annotated

from pydantic import Field

from thrs.classes.control import ControlMode
from thrs.control.modules.consumers.io import ConsumersControlValues
from thrs.control.state import ControlState
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.controllers import PidControllerValues
from thrs.input_output.definitions.units import Ratio, Tuning


class ConsumersControlMode(ControlMode):
    pass


class ConsumersParameters(ThrsValues):
    dhw_enabled: bool = True
    dhw_flow_ratio_setpoint: Annotated[Ratio, Field(ge=0.0, le=1.0)] = 0.3
    adsorption_enabled: bool = True
    adsorption_flow_ratio_setpoint: Annotated[Ratio, Field(ge=0.0, le=1.0)] = 0.3
    dhw_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    bypass_flow_balance_tuning: Tuning = (0.01, 0.001, 0)
    adsorption_flow_balance_tuning: Tuning = (0.01, 0.001, 0)


class ConsumersControllerState(
    ControlState[ConsumersControlValues, ConsumersParameters, ConsumersControlMode]
):
    consumers_dhw_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    consumers_bypass_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
    consumers_adsorption_flow_controller: Annotated[
        PidControllerValues, component_meta(component_type="pid_controller")
    ]
