import strawberry

from thrs.control.modules.pcm import PcmParameters
from thrs.graphql.base import (
    JsonSchemaDirective,
    Module,
    ModuleSimulation,
    PcmMessaging,
    add_control_mutations,
    add_parameter_mutations,
    add_simulation_input_mutations,
    ensure_dedataframes,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)


@strawberry.experimental.pydantic.type(
    model=PcmSensorValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class PcmSensorValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=PcmControlValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class PcmControlValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=PcmParameters,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class PcmParametersType:
    pass


DedataframedSimulationInputs = PcmSimulationInputs.dedataframe()
DedataframedSimulationOutputs = PcmSimulationOutputs.dedataframe()

ensure_dedataframes(DedataframedSimulationInputs)
ensure_dedataframes(DedataframedSimulationOutputs)


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationInputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class PcmSimulationInputsType:
    pass


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationOutputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
)
class PcmSimulationOutputsType:
    pass


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
        sensor_values=(
            PcmSensorValuesType.from_pydantic(module.sensor_values)
            if module.sensor_values
            else None
        ),
        control_values=(
            PcmControlValuesType.from_pydantic(module.control_values)
            if module.control_values
            else None
        ),
        parameters=(
            PcmParametersType.from_pydantic(module.parameters)
            if module.parameters
            else None
        ),
        simulation=ModuleSimulation(
            inputs=(
                PcmSimulationInputsType.from_pydantic(module.simulation_inputs)
                if module.simulation_inputs
                else None
            ),
            outputs=PcmSimulationOutputsType.from_pydantic(
                DedataframedSimulationOutputs.zero()  # TODO: ZERO-927 implement simulation output setting and passage to simulation
            ),
        ),
    )


def get_pcm_messaging(context):
    return context.pcm_messaging


@strawberry.type
@add_control_mutations(PcmControlValues, PcmControlValuesType, get_pcm_messaging)
@add_parameter_mutations(PcmParameters, PcmParametersType, get_pcm_messaging)
@add_simulation_input_mutations(
    PcmSimulationInputs, PcmSimulationInputsType, get_pcm_messaging
)
class PcmMutations:
    pass
