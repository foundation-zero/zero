import strawberry

from thrs.control.modules.drives import (
    DrivesControllerState,
    DrivesControlMode,
    DrivesParameters,
)
from thrs.graphql.base import (
    ControlModule,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    empty_pydantic_type_to_strawberry_type,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.drives import DrivesControlValues, DrivesSensorValues

DrivesSensorValuesType = pydantic_to_strawberry_type(
    DrivesSensorValues, include_computed=True
)
DrivesControlValuesType = pydantic_to_strawberry_type(DrivesControlValues)
DrivesParametersType = pydantic_to_strawberry_type(DrivesParameters)
DrivesControlModeType = pydantic_to_strawberry_type(DrivesControlMode)
DrivesControllerStateType = empty_pydantic_type_to_strawberry_type(
    DrivesControllerState
)


DrivesModule = ControlModule[
    DrivesSensorValuesType,
    DrivesControlValuesType,
    DrivesParametersType,
    DrivesControlModeType,
    DrivesControllerStateType,
]


def get_drives_messaging(context):
    return context.drives_messaging


@strawberry.type
@add_control_mutations(
    "drives",
    DrivesControlValues,
    DrivesControlValuesType,
    get_drives_messaging,
)
@add_parameter_mutations(
    "drives", DrivesParameters, DrivesParametersType, get_drives_messaging
)
@add_automation_mode_mutation("drives", get_drives_messaging)
class DrivesMutations:
    pass
