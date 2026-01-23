import strawberry

from thrs.control.modules.pvt import PvtParameters
from thrs.graphql.base import (
    Module,
    PvtMessaging,
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
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)


PvtSensorValuesType = pydantic_to_strawberry_type(PvtSensorValues)
PvtControlValuesType = pydantic_to_strawberry_type(PvtControlValues)
PvtParametersType = pydantic_to_strawberry_type(PvtParameters)

PvtSimulationInputsType = dedataframed_pydantic_to_strawberry_type(PvtSimulationInputs)
PvtSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    PvtSimulationOutputs
)


PvtModule = Module[
    PvtSensorValuesType,
    PvtControlValuesType,
    PvtParametersType,
]


def resolve_module(
    module: PvtMessaging,
) -> PvtModule:
    return Module(
        sensor_values=optional_pydantic_to_graphql(
            PvtSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            PvtControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(PvtParametersType, module.parameters),
        automatic=module.control_status.automatic if module.control_status else None,
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
