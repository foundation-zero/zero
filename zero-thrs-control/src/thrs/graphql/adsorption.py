import strawberry

from thrs.control.modules.adsorption import AdsorptionControlMode, AdsorptionParameters
from thrs.graphql.base import (
    AdsorptionMessaging,
    ControlModule,
    SwitchingControlModeType,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
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


@strawberry.type()
class AdsorptionControllerStateType:
    _empty: None = None

    @classmethod
    def from_pydantic(cls, _type) -> "AdsorptionControllerStateType":
        return cls()


AdsorptionModule = ControlModule[
    AdsorptionSensorValuesType,
    AdsorptionControlValuesType,
    AdsorptionParametersType,
    AdsorptionControlModeType,
    AdsorptionControllerStateType,
]


def resolve_module(
    module: AdsorptionMessaging,
) -> AdsorptionModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            AdsorptionSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            AdsorptionControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(
            AdsorptionParametersType, module.parameters
        ),
        control_mode=SwitchingControlModeType.from_pydantic(
            AdsorptionControlModeType, module.control_mode
        )
        if module.control_mode
        else None,
        controller_state=optional_pydantic_to_graphql(
            AdsorptionControllerStateType, module.controller_state
        ),
    )


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
