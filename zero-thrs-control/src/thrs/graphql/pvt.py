import strawberry

from thrs.control.modules.pvt import PvtControlMode, PvtGroupControlMode, PvtParameters
from thrs.graphql.base import (
    PvtMessaging,
    SwitchingControlModeType,
    ThrsContext,
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
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
)


PvtSensorValuesType = pydantic_to_strawberry_type(PvtSensorValues)
PvtControlValuesType = pydantic_to_strawberry_type(PvtControlValues)
PvtParametersType = pydantic_to_strawberry_type(PvtParameters)
PvtGroupControlModeType = pydantic_to_strawberry_type(PvtGroupControlMode)
PvtControlModeType = pydantic_to_strawberry_type(PvtControlMode)


PvtModule = ControlModule[
    PvtSensorValuesType,
    PvtControlValuesType,
    PvtParametersType,
    PvtControlModeType,
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
        parameters=(
            PvtParametersType.from_pydantic(module.parameters)
            if module.parameters
            else None
        ),
        control_mode=SwitchingControlModeType.from_pydantic(
            PvtControlModeType, module.control_mode.mode
        )
        if module.control_mode
        else None,
    )


def get_pvt_messaging(context: ThrsContext):
    return context.pvt_messaging


@strawberry.type
@add_control_mutations("pvt", PvtControlValues, PvtControlValuesType, get_pvt_messaging)
@add_parameter_mutations("pvt", PvtParameters, PvtParametersType, get_pvt_messaging)
@add_automation_mode_mutation("pvt", get_pvt_messaging)
class PvtMutations:
    pass
