import strawberry

from thrs.control.modules.pvt import PvtControllerState, PvtControlMode, PvtParameters
from thrs.control.modules.pvt_group import PvtGroupControlMode
from thrs.graphql.base import (
    ControlModule,
    ThrsContext,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import pydantic_to_strawberry_type
from thrs.input_output.modules.pvt import PvtControlValues, PvtSensorValues

PvtSensorValuesType = pydantic_to_strawberry_type(
    PvtSensorValues, include_computed=True
)
PvtControlValuesType = pydantic_to_strawberry_type(PvtControlValues)
PvtParametersType = pydantic_to_strawberry_type(PvtParameters)
PvtGroupControlModeType = pydantic_to_strawberry_type(PvtGroupControlMode)
PvtControlModeType = pydantic_to_strawberry_type(PvtControlMode)
PvtControllerStateType = pydantic_to_strawberry_type(PvtControllerState)


PvtModule = ControlModule[
    PvtSensorValuesType,
    PvtControlValuesType,
    PvtParametersType,
    PvtControlModeType,
    PvtControllerStateType,
]


def get_pvt_messaging(context: ThrsContext):
    return context.pvt_messaging


@strawberry.type
@add_control_mutations("pvt", PvtControlValues, PvtControlValuesType, get_pvt_messaging)
@add_parameter_mutations("pvt", PvtParameters, PvtParametersType, get_pvt_messaging)
@add_automation_mode_mutation("pvt", get_pvt_messaging)
class PvtMutations:
    pass
