import strawberry

from thrs.control.modules.consumers import (
    ConsumersControllerValues,
    ConsumersParameters,
)
from thrs.graphql.base import (
    ConsumersMessaging,
    ControlModule,
    SwitchingControllerValuesType,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)

ConsumersSensorValuesType = pydantic_to_strawberry_type(ConsumersSensorValues)
ConsumersControlValuesType = pydantic_to_strawberry_type(ConsumersControlValues)
ConsumersParametersType = pydantic_to_strawberry_type(ConsumersParameters)
ConsumersControllerValuesType = pydantic_to_strawberry_type(ConsumersControllerValues)


@strawberry.type()
class ConsumersControlModeType:
    _empty: None = None


ConsumersModule = ControlModule[
    ConsumersSensorValuesType,
    ConsumersControlValuesType,
    ConsumersParametersType,
    ConsumersControllerValuesType,
]


def resolve_module(
    module: ConsumersMessaging,
) -> ConsumersModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            ConsumersSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            ConsumersControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(
            ConsumersParametersType, module.parameters
        ),
        controller_values=optional_pydantic_to_graphql(
            SwitchingControllerValuesType[ConsumersControllerValuesType],
            module.controller_values,
        ),
    )


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
