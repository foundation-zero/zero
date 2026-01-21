import strawberry

from thrs.control.modules.pcm import PcmParameters
from thrs.graphql.base import (
    Module,
    ModuleSimulation,
    PcmMessaging,
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
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)


PcmSensorValuesType = pydantic_to_strawberry_type(PcmSensorValues)
PcmControlValuesType = pydantic_to_strawberry_type(PcmControlValues)
PcmParametersType = pydantic_to_strawberry_type(PcmParameters)

PcmSimulationInputsType = dedataframed_pydantic_to_strawberry_type(PcmSimulationInputs)
PcmSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    PcmSimulationOutputs
)


PcmModule = Module[
    PcmSensorValuesType,
    PcmControlValuesType,
    PcmParametersType,
    PcmSimulationInputsType,
    PcmSimulationOutputsType,
]


def resolve_module(
    module: PcmMessaging,
) -> PcmModule:
    return Module(
        sensor_values=optional_pydantic_to_graphql(
            PcmSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            PcmControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(PcmParametersType, module.parameters),
        simulation=ModuleSimulation(
            inputs=optional_pydantic_to_graphql(
                PcmSimulationInputsType, module.simulation_inputs
            ),
            outputs=optional_pydantic_to_graphql(
                PcmSimulationOutputsType, module.simulation_outputs
            ),
        ),
        automatic=module.control_status.automatic if module.control_status else None,
    )


def get_pcm_messaging(context):
    return context.pcm_messaging


@strawberry.type
@add_control_mutations("pcm", PcmControlValues, PcmControlValuesType, get_pcm_messaging)
@add_parameter_mutations("pcm", PcmParameters, PcmParametersType, get_pcm_messaging)
@add_simulation_input_mutations(
    "pcm", PcmSimulationInputs, PcmSimulationInputsType, get_pcm_messaging
)
@add_automation_mode_mutation("pcm", get_pcm_messaging)
class PcmMutations:
    pass
