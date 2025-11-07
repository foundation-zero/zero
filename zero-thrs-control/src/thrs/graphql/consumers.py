import strawberry

from thrs.control.modules.consumers import ConsumersParameters
from thrs.graphql.base import (
    JsonSchemaDirective,
    Module,
    ModuleSimulation,
    ConsumersMessaging,
    add_control_mutations,
    add_parameter_mutations,
    add_simulation_input_mutations,
    ensure_dedataframes,
)
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)


@strawberry.experimental.pydantic.type(
    model=ConsumersSensorValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ConsumersSensorValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=ConsumersControlValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ConsumersControlValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=ConsumersParameters,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ConsumersParametersType:
    pass


DedataframedSimulationInputs = ConsumersSimulationInputs.dedataframe()
DedataframedSimulationOutputs = ConsumersSimulationOutputs.dedataframe()

ensure_dedataframes(DedataframedSimulationInputs)
ensure_dedataframes(DedataframedSimulationOutputs)


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationInputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ConsumersSimulationInputsType:
    pass


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationOutputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class ConsumersSimulationOutputsType:
    pass


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
        sensor_values=(
            ConsumersSensorValuesType.from_pydantic(module.sensor_values)
            if module.sensor_values
            else None
        ),
        control_values=(
            ConsumersControlValuesType.from_pydantic(module.control_values)
            if module.control_values
            else None
        ),
        parameters=(
            ConsumersParametersType.from_pydantic(module.parameters)
            if module.parameters
            else None
        ),
        simulation=ModuleSimulation(
            inputs=(
                ConsumersSimulationInputsType.from_pydantic(module.simulation_inputs)
                if module.simulation_inputs
                else None
            ),
            outputs=ConsumersSimulationOutputsType.from_pydantic(
                DedataframedSimulationOutputs.zero()  # TODO: ZERO-927 implement simulation output setting and passage to simulation
            ),
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
@add_simulation_input_mutations(
    "consumers",
    ConsumersSimulationInputs,
    ConsumersSimulationInputsType,
    get_consumers_messaging,
)
class ConsumersMutations:
    pass
