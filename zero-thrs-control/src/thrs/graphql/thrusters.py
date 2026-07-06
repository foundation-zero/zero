import strawberry

from thrs.control.modules.thrusters import (
    ThrustersControlMode,
    ThrustersParameters,
)
from thrs.graphql.base import (
    ControlModule,
    SwitchingControlModeType,
    ThrsContext,
    ThrustersMessaging,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)

ThrustersSensorValuesType = pydantic_to_strawberry_type(ThrustersSensorValues)
ThrustersControlValuesType = pydantic_to_strawberry_type(ThrustersControlValues)
ThrustersParametersType = pydantic_to_strawberry_type(ThrustersParameters)
ThrustersControlModeType = pydantic_to_strawberry_type(ThrustersControlMode)


@strawberry.type()
class ThrustersControllerStateType:
    _empty: None = None


ThrustersModule = ControlModule[
    ThrustersSensorValuesType,
    ThrustersControlValuesType,
    ThrustersParametersType,
    ThrustersControlModeType,
    ThrustersControllerStateType,
]


def resolve_module(
    module: ThrustersMessaging,
) -> ThrustersModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            ThrustersSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            ThrustersControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(
            ThrustersParametersType, module.parameters
        ),
        control_mode=SwitchingControlModeType.from_pydantic(
            ThrustersControlModeType, module.control_mode
        )
        if module.control_mode
        else None,
        controller_state=ThrustersControllerStateType(),
    )


def get_thrusters_messaging(context: ThrsContext) -> ThrustersMessaging:
    return context.thrusters_messaging


@strawberry.type
@add_control_mutations(
    "thrusters",
    ThrustersControlValues,
    ThrustersControlValuesType,
    get_thrusters_messaging,
)
@add_parameter_mutations(
    "thrusters", ThrustersParameters, ThrustersParametersType, get_thrusters_messaging
)
@add_automation_mode_mutation("thrusters", get_thrusters_messaging)
class ThrustersMutations:
    pass
