import strawberry

from thrs.control.modules.thrusters import ThrustersParameters
from thrs.graphql.base import (
    JsonSchemaDirective,
    Module,
    ModuleSimulation,
    ThrustersMessaging,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
    add_simulation_input_mutations,
    ensure_dedataframes,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)


@strawberry.experimental.pydantic.type(
    model=ThrustersSensorValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class ThrustersSensorValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=ThrustersControlValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class ThrustersControlValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=ThrustersParameters,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class ThrustersParametersType:
    pass


DedataframedSimulationInputs = ThrustersSimulationInputs.dedataframe()
DedataframedSimulationOutputs = ThrustersSimulationOutputs.dedataframe()

ensure_dedataframes(DedataframedSimulationInputs)
ensure_dedataframes(DedataframedSimulationOutputs)


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationInputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class ThrustersSimulationInputsType:
    pass


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationOutputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class ThrustersSimulationOutputsType:
    pass


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
        sensor_values=(
            ThrustersSensorValuesType.from_pydantic(module.sensor_values)
            if module.sensor_values
            else None
        ),
        control_values=(
            ThrustersControlValuesType.from_pydantic(module.control_values)
            if module.control_values
            else None
        ),
        parameters=(
            ThrustersParametersType.from_pydantic(module.parameters)
            if module.parameters
            else None
        ),
        simulation=ModuleSimulation(
            inputs=(
                ThrustersSimulationInputsType.from_pydantic(module.simulation_inputs)
                if module.simulation_inputs
                else None
            ),
            outputs=ThrustersSimulationOutputsType.from_pydantic(
                module.simulation_outputs
            )
            if module.simulation_outputs
            else None,
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
