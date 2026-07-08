import strawberry

from thrs.control.modules.dc import DcControlMode, DcParameters
from thrs.graphql.base import (
    ControlModule,
    DcMessaging,
    SwitchingControlModeType,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.dc import (
    DcControlValues,
    DcSensorValues,
)

DcSensorValuesType = pydantic_to_strawberry_type(DcSensorValues, include_computed=True)
DcControlValuesType = pydantic_to_strawberry_type(DcControlValues)
DcParametersType = pydantic_to_strawberry_type(DcParameters)
DcControlModeType = pydantic_to_strawberry_type(DcControlMode)


@strawberry.type()
class DcControllerStateType:
    _empty: None = None


DcModule = ControlModule[
    DcSensorValuesType,
    DcControlValuesType,
    DcParametersType,
    DcControlModeType,
    DcControllerStateType,
]


def resolve_module(
    module: DcMessaging,
) -> DcModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            DcSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            DcControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(DcParametersType, module.parameters),
        control_mode=SwitchingControlModeType.from_pydantic(
            DcControlModeType, module.control_mode
        )
        if module.control_mode
        else None,
        controller_state=optional_pydantic_to_graphql(
            DcControllerStateType, module.controller_state
        ),
    )


def get_dc_messaging(context):
    return context.dc_messaging


@strawberry.type
@add_control_mutations(
    "dc",
    DcControlValues,
    DcControlValuesType,
    get_dc_messaging,
)
@add_parameter_mutations("dc", DcParameters, DcParametersType, get_dc_messaging)
@add_automation_mode_mutation("dc", get_dc_messaging)
class DcMutations:
    pass
