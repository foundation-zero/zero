import strawberry

from thrs.control.modules.thrusters import (
    ThrustersControllerState,
    ThrustersControlMode,
    ThrustersParameters,
)
from thrs.graphql.base import (
    ControlModule,
    ThrsContext,
    ThrustersMessaging,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import pydantic_to_strawberry_type
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)

ThrustersSensorValuesType = pydantic_to_strawberry_type(
    ThrustersSensorValues, include_computed=True
)
ThrustersControlValuesType = pydantic_to_strawberry_type(ThrustersControlValues)
ThrustersParametersType = pydantic_to_strawberry_type(ThrustersParameters)
ThrustersControlModeType = pydantic_to_strawberry_type(ThrustersControlMode)
ThrustersControllerStateType = pydantic_to_strawberry_type(ThrustersControllerState)


ThrustersModule = ControlModule[
    ThrustersSensorValuesType,
    ThrustersControlValuesType,
    ThrustersParametersType,
    ThrustersControlModeType,
    ThrustersControllerStateType,
]


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
