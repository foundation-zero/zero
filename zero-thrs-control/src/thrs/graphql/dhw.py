import strawberry

from thrs.control.modules.dhw import DhwControllerState, DhwControlMode, DhwParameters
from thrs.graphql.base import (
    ControlModule,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import pydantic_to_strawberry_type
from thrs.input_output.modules.dhw import DhwControlValues, DhwSensorValues

DhwSensorValuesType = pydantic_to_strawberry_type(
    DhwSensorValues, include_computed=True
)
DhwControlValuesType = pydantic_to_strawberry_type(DhwControlValues)
DhwParametersType = pydantic_to_strawberry_type(DhwParameters)
DhwControlModeType = pydantic_to_strawberry_type(DhwControlMode)
DhwControllerStateType = pydantic_to_strawberry_type(DhwControllerState)


DhwModule = ControlModule[
    DhwSensorValuesType,
    DhwControlValuesType,
    DhwParametersType,
    DhwControlModeType,
    DhwControllerStateType,
]


def get_dhw_messaging(context):
    return context.dhw_messaging


@strawberry.type
@add_control_mutations(
    "dhw",
    DhwControlValues,
    DhwControlValuesType,
    get_dhw_messaging,
)
@add_parameter_mutations("dhw", DhwParameters, DhwParametersType, get_dhw_messaging)
@add_automation_mode_mutation("dhw", get_dhw_messaging)
class DhwMutations:
    pass
