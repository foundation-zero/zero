import strawberry

from thrs.control.modules.pvt import PvtControllerValues, PvtControlMode, PvtParameters
from thrs.control.modules.pvt_group import PvtGroupControlMode
from thrs.graphql.base import (
    ControlModule,
    PvtMessaging,
    SwitchingControllerValuesType,
    ThrsContext,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
)

PvtSensorValuesType = pydantic_to_strawberry_type(PvtSensorValues)
PvtControlValuesType = pydantic_to_strawberry_type(PvtControlValues)
PvtParametersType = pydantic_to_strawberry_type(PvtParameters)
PvtGroupControlModeType = pydantic_to_strawberry_type(PvtGroupControlMode)
PvtControlModeType = pydantic_to_strawberry_type(PvtControlMode)
PvtControllerValuesType = pydantic_to_strawberry_type(PvtControllerValues)


PvtModule = ControlModule[
    PvtSensorValuesType,
    PvtControlValuesType,
    PvtParametersType,
    PvtControllerValuesType,
]


def resolve_module(
    module: PvtMessaging,
) -> PvtModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            PvtSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            PvtControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(PvtParametersType, module.parameters),
        controller_values=optional_pydantic_to_graphql(
            SwitchingControllerValuesType[PvtControllerValuesType],
            module.controller_values,
        ),
    )


def get_pvt_messaging(context: ThrsContext):
    return context.pvt_messaging


@strawberry.type
@add_control_mutations("pvt", PvtControlValues, PvtControlValuesType, get_pvt_messaging)
@add_parameter_mutations("pvt", PvtParameters, PvtParametersType, get_pvt_messaging)
@add_automation_mode_mutation("pvt", get_pvt_messaging)
class PvtMutations:
    pass
