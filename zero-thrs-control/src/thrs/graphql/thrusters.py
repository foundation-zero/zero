import strawberry

from thrs.control.modules.thrusters import ThrustersParameters
from thrs.graphql.base import (
    Module,
    ModuleSimulation,
    ThrustersMessaging,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
    add_simulation_input_mutations,
)
from thrs.graphql.helpers import (
    pydantic_to_strawberry_type,
    create_simulation_type,
    optional_convert,
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

ThrustersSimulationInputsType = create_simulation_type(ThrustersSimulationInputs)
ThrustersSimulationOutputsType = create_simulation_type(ThrustersSimulationOutputs)


ThrustersModule = Module[
    ThrustersSensorValuesType,
    ThrustersControlValuesType,
    ThrustersParametersType,
    ThrustersSimulationInputsType,
    ThrustersSimulationOutputsType,
]


def resolve_module(
    module: ThrustersMessaging,
) -> ThrustersModule:
    return Module(
        sensor_values=optional_convert(ThrustersSensorValuesType, module.sensor_values),
        control_values=optional_convert(
            ThrustersControlValuesType, module.control_values
        ),
        parameters=optional_convert(ThrustersParametersType, module.parameters),
        simulation=ModuleSimulation(
            inputs=optional_convert(
                ThrustersSimulationInputsType, module.simulation_inputs
            ),
            outputs=optional_convert(
                ThrustersSimulationOutputsType, module.simulation_outputs
            ),
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
