import strawberry

from thrs.control.modules.consumers import (
    ConsumersControllerState,
    ConsumersControlMode,
    ConsumersParameters,
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
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)

ConsumersSensorValuesType = pydantic_to_strawberry_type(
    ConsumersSensorValues, include_computed=True
)
ConsumersControlValuesType = pydantic_to_strawberry_type(ConsumersControlValues)
ConsumersParametersType = pydantic_to_strawberry_type(ConsumersParameters)
ConsumersControlModeType = empty_pydantic_type_to_strawberry_type(ConsumersControlMode)
ConsumersControllerStateType = empty_pydantic_type_to_strawberry_type(
    ConsumersControllerState
)


ConsumersModule = ControlModule[
    ConsumersSensorValuesType,
    ConsumersControlValuesType,
    ConsumersParametersType,
    ConsumersControlModeType,
    ConsumersControllerStateType,
]


def get_consumers_messaging(context):
    return context.consumers_messaging


@strawberry.type
@add_control_mutations(
    "consumers",
    ConsumersControlValues,
    ConsumersControlValuesType,
    get_consumers_messaging,
)
@add_parameter_mutations(
    "consumers", ConsumersParameters, ConsumersParametersType, get_consumers_messaging
)
@add_automation_mode_mutation("consumers", get_consumers_messaging)
class ConsumersMutations:
    pass
