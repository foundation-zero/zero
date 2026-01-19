import strawberry

from thrs.control.modules.pvt import PvtControlMode, PvtGroupControlMode, PvtParameters
from thrs.graphql.base import (
    JsonSchemaDirective,
    Module,
    ModuleSimulation,
    PvtMessaging,
    SwitchingControlModeType,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
    add_simulation_input_mutations,
    ensure_dedataframes,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)


@strawberry.experimental.pydantic.type(
    model=PvtSensorValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class PvtSensorValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=PvtControlValues,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class PvtControlValuesType:
    pass


@strawberry.experimental.pydantic.type(
    model=PvtParameters,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class PvtParametersType:
    pass


DedataframedSimulationInputs = PvtSimulationInputs.dedataframe()
DedataframedSimulationOutputs = PvtSimulationOutputs.dedataframe()

ensure_dedataframes(DedataframedSimulationInputs)
ensure_dedataframes(DedataframedSimulationOutputs)


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationInputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class PvtSimulationInputsType:
    pass


@strawberry.experimental.pydantic.type(
    model=DedataframedSimulationOutputs,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class PvtSimulationOutputsType:
    pass


@strawberry.experimental.pydantic.type(
    model=PvtGroupControlMode,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class PvtGroupControlModeType:
    pass


@strawberry.experimental.pydantic.type(
    model=PvtControlMode,
    all_fields=True,
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class PvtControlModeType:
    pass


PvtModule = Module[
    PvtSensorValuesType,
    PvtControlValuesType,
    PvtParametersType,
    PvtSimulationInputsType,
    PvtSimulationOutputsType,
    PvtControlModeType,
]


def resolve_module(
    module: PvtMessaging,
) -> PvtModule:
    return Module(
        sensor_values=(
            PvtSensorValuesType.from_pydantic(module.sensor_values)
            if module.sensor_values
            else None
        ),
        control_values=(
            PvtControlValuesType.from_pydantic(module.control_values)
            if module.control_values
            else None
        ),
        parameters=(
            PvtParametersType.from_pydantic(module.parameters)
            if module.parameters
            else None
        ),
        simulation=ModuleSimulation(
            inputs=(
                PvtSimulationInputsType.from_pydantic(module.simulation_inputs)
                if module.simulation_inputs
                else None
            ),
            outputs=PvtSimulationOutputsType.from_pydantic(module.simulation_outputs)
            if module.simulation_outputs
            else None,
        ),
        control_mode=SwitchingControlModeType.from_pydantic(
            PvtControlModeType, module.control_status.mode
        )
        if module.control_status
        else None,
    )


def get_pvt_messaging(context):
    return context.pvt_messaging


@strawberry.type
@add_control_mutations("pvt", PvtControlValues, PvtControlValuesType, get_pvt_messaging)
@add_parameter_mutations("pvt", PvtParameters, PvtParametersType, get_pvt_messaging)
@add_simulation_input_mutations(
    "pvt", PvtSimulationInputs, PvtSimulationInputsType, get_pvt_messaging
)
@add_automation_mode_mutation("pvt", get_pvt_messaging)
class PvtMutations:
    pass
