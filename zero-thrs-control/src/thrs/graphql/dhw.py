import strawberry

from thrs.control.modules.dhw import DhwControlMode, DhwParameters
from thrs.graphql.base import (
    ControlModule,
    DhwMessaging,
    SwitchingControlModeType,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.dhw import DhwControlValues, DhwSensorValues

DhwSensorValuesType = pydantic_to_strawberry_type(
    DhwSensorValues, include_computed=True
)
DhwControlValuesType = pydantic_to_strawberry_type(DhwControlValues)
DhwParametersType = pydantic_to_strawberry_type(DhwParameters)
DhwControlModeType = pydantic_to_strawberry_type(DhwControlMode)


DhwModule = ControlModule[
    DhwSensorValuesType,
    DhwControlValuesType,
    DhwParametersType,
    DhwControlModeType,
]


def resolve_module(
    module: DhwMessaging,
) -> DhwModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            DhwSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            DhwControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(DhwParametersType, module.parameters),
        control_mode=SwitchingControlModeType.from_pydantic(
            DhwControlModeType, module.control_mode.mode
        )
        if module.control_mode
        else None,
    )


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
