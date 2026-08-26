import strawberry

from thrs.control.modules.adsorption import (
    AdsorptionControllerState,
    AdsorptionControlMode,
    AdsorptionParameters,
)
from thrs.graphql.base import (
    ControlModule,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    empty_pydantic_type_to_strawberry_type,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.adsorption import (
    AdsorptionControlValues,
    AdsorptionSensorValues,
)

AdsorptionSensorValuesType = pydantic_to_strawberry_type(
    AdsorptionSensorValues, include_computed=True
)
AdsorptionControlValuesType = pydantic_to_strawberry_type(AdsorptionControlValues)
AdsorptionParametersType = pydantic_to_strawberry_type(AdsorptionParameters)
AdsorptionControlModeType = pydantic_to_strawberry_type(AdsorptionControlMode)
AdsorptionControllerStateType = empty_pydantic_type_to_strawberry_type(
    AdsorptionControllerState
)


AdsorptionModule = ControlModule[
    AdsorptionSensorValuesType,
    AdsorptionControlValuesType,
    AdsorptionParametersType,
    AdsorptionControlModeType,
    AdsorptionControllerStateType,
]


def get_adsorption_messaging(context):
    return context.adsorption_messaging


@strawberry.type
@add_control_mutations(
    "adsorption",
    AdsorptionControlValues,
    AdsorptionControlValuesType,
    get_adsorption_messaging,
)
@add_parameter_mutations(
    "adsorption",
    AdsorptionParameters,
    AdsorptionParametersType,
    get_adsorption_messaging,
)
@add_automation_mode_mutation("adsorption", get_adsorption_messaging)
class AdsorptionMutations:
    pass
