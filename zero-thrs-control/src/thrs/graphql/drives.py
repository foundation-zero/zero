import strawberry

from thrs.control.modules.drives import DrivesControlMode, DrivesParameters
from thrs.graphql.base import (
    ControlModule,
    DrivesMessaging,
    SwitchingControlModeType,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.drives import (
    DrivesControlValues,
    DrivesSensorValues,
)

DrivesSensorValuesType = pydantic_to_strawberry_type(
    DrivesSensorValues, include_computed=True
)
DrivesControlValuesType = pydantic_to_strawberry_type(DrivesControlValues)
DrivesParametersType = pydantic_to_strawberry_type(DrivesParameters)
DrivesControlModeType = pydantic_to_strawberry_type(DrivesControlMode)


@strawberry.type()
class DrivesControllerStateType:
    _empty: None = None


DrivesModule = ControlModule[
    DrivesSensorValuesType,
    DrivesControlValuesType,
    DrivesParametersType,
    DrivesControlModeType,
    DrivesControllerStateType,
]


def resolve_module(
    module: DrivesMessaging,
) -> DrivesModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            DrivesSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            DrivesControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(
            DrivesParametersType, module.parameters
        ),
        control_mode=SwitchingControlModeType.from_pydantic(
            DrivesControlModeType, module.control_mode
        )
        if module.control_mode
        else None,
        controller_state=optional_pydantic_to_graphql(
            DrivesControllerStateType, module.controller_state
        ),
    )


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
