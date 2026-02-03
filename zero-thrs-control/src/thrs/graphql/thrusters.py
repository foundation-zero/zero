import strawberry

from thrs.control.modules.thrusters import ThrustersControlMode, ThrustersParameters
from thrs.graphql.base import (
    SwitchingControlModeType,
    ThrsContext,
    ThrustersMessaging,
    add_automation_mode_mutation,
)
from thrs.graphql.base import (
    ControlModule,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    pydantic_to_strawberry_type,
    optional_pydantic_to_graphql,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)

ThrustersSensorValuesType = pydantic_to_strawberry_type(ThrustersSensorValues)
ThrustersControlValuesType = pydantic_to_strawberry_type(ThrustersControlValues)
ThrustersParametersType = pydantic_to_strawberry_type(ThrustersParameters)
ThrustersControlModeType = pydantic_to_strawberry_type(ThrustersControlMode)


ThrustersModule = ControlModule[
    ThrustersSensorValuesType,
    ThrustersControlValuesType,
    ThrustersParametersType,
    ThrustersControlModeType,
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
            ThrustersControlModeType, module.control_mode.mode
        )
        if module.control_mode
        else None,
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
