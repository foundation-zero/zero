import strawberry

from thrs.control.modules.consumers import ConsumersParameters
from thrs.graphql.base import (
    Module,
    ModuleSimulation,
    ConsumersMessaging,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
    add_simulation_input_mutations,
)
from thrs.graphql.helpers import (
    pydantic_to_strawberry_type,
    dedataframed_pydantic_to_strawberry_type,
    optional_pydantic_to_graphql,
)
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)


ConsumersSensorValuesType = pydantic_to_strawberry_type(ConsumersSensorValues)
ConsumersControlValuesType = pydantic_to_strawberry_type(ConsumersControlValues)
ConsumersParametersType = pydantic_to_strawberry_type(ConsumersParameters)

ConsumersSimulationInputsType = dedataframed_pydantic_to_strawberry_type(
    ConsumersSimulationInputs
)
ConsumersSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    ConsumersSimulationOutputs
)


ConsumersModule = Module[
    ConsumersSensorValuesType,
    ConsumersControlValuesType,
    ConsumersParametersType,
    ConsumersSimulationInputsType,
    ConsumersSimulationOutputsType,
]


def resolve_module(
    module: ConsumersMessaging,
) -> ConsumersModule:
    return Module(
        sensor_values=optional_pydantic_to_graphql(
            ConsumersSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            ConsumersControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(
            ConsumersParametersType, module.parameters
        ),
        simulation=ModuleSimulation(
            inputs=optional_pydantic_to_graphql(
                ConsumersSimulationInputsType, module.simulation_inputs
            ),
            outputs=optional_pydantic_to_graphql(
                ConsumersSimulationOutputsType, module.simulation_outputs
            ),
        ),
        automatic=module.control_status.automatic if module.control_status else None,
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
@add_simulation_input_mutations(
    "consumers",
    ConsumersSimulationInputs,
    ConsumersSimulationInputsType,
    get_consumers_messaging,
)
@add_automation_mode_mutation("consumers", get_consumers_messaging)
class ConsumersMutations:
    pass
