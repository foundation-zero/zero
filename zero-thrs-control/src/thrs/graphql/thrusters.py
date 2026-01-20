import strawberry

from thrs.control.modules.thrusters import ThrustersParameters
from thrs.graphql.base import (
    Module,
    ThrustersMessaging,
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
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)


ThrustersSensorValuesType = pydantic_to_strawberry_type(ThrustersSensorValues)
ThrustersControlValuesType = pydantic_to_strawberry_type(ThrustersControlValues)
ThrustersParametersType = pydantic_to_strawberry_type(ThrustersParameters)

ThrustersSimulationInputsType = dedataframed_pydantic_to_strawberry_type(
    ThrustersSimulationInputs
)
ThrustersSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    ThrustersSimulationOutputs
)


ThrustersModule = Module[
    ThrustersSensorValuesType,
    ThrustersControlValuesType,
    ThrustersParametersType,
]


def resolve_module(
    module: ThrustersMessaging,
) -> ThrustersModule:
    return Module(
        sensor_values=optional_pydantic_to_graphql(
            ThrustersSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            ThrustersControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(
            ThrustersParametersType, module.parameters
        ),
        automatic=module.control_status.automatic if module.control_status else None,
    )


def get_thrusters_messaging(context):
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
@add_simulation_input_mutations(
    "thrusters",
    ThrustersSimulationInputs,
    ThrustersSimulationInputsType,
    get_thrusters_messaging,
)
@add_automation_mode_mutation("thrusters", get_thrusters_messaging)
class ThrustersMutations:
    pass
