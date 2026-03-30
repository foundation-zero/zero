import strawberry

from thrs.control.modules.boilers import BoilersParameters
from thrs.graphql.base import (
    BoilersMessaging,
    SwitchingControlModeType,
)
from thrs.graphql.base import (
    ControlModule,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    pydantic_to_strawberry_type,
    optional_pydantic_to_graphql,
)
from thrs.input_output.modules.boilers import BoilersControlValues, BoilersSensorValues


BoilersSensorValuesType = pydantic_to_strawberry_type(BoilersSensorValues)
BoilersControlValuesType = pydantic_to_strawberry_type(BoilersControlValues)
BoilersParametersType = pydantic_to_strawberry_type(BoilersParameters)


@strawberry.type()
class BoilersControlModeType:
    _empty: None = None


BoilersModule = ControlModule[
    BoilersSensorValuesType,
    BoilersControlValuesType,
    BoilersParametersType,
    BoilersControlModeType,
]


def resolve_module(
    module: BoilersMessaging,
) -> BoilersModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            BoilersSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            BoilersControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(
            BoilersParametersType, module.parameters
        ),
        control_mode=SwitchingControlModeType.from_pydantic(
            BoilersControlModeType, module.control_mode.mode
        )
        if module.control_mode
        else None,
    )


def get_boilers_messaging(context):
    return context.boilers_messaging


@strawberry.type
@add_control_mutations(
    "boilers",
    BoilersControlValues,
    BoilersControlValuesType,
    get_boilers_messaging,
)
@add_parameter_mutations(
    "boilers", BoilersParameters, BoilersParametersType, get_boilers_messaging
)
@add_automation_mode_mutation("boilers", get_boilers_messaging)
class BoilersMutations:
    pass
