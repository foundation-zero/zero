import strawberry

from thrs.control.modules.pcm import PcmControllerState, PcmControlMode, PcmParameters
from thrs.graphql.base import (
    ControlModule,
    PcmMessaging,
    SwitchingControlModeType,
    add_automation_mode_mutation,
    add_control_mutations,
    add_parameter_mutations,
)
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
    pydantic_to_strawberry_type,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
)

PcmSensorValuesType = pydantic_to_strawberry_type(PcmSensorValues)
PcmControlValuesType = pydantic_to_strawberry_type(PcmControlValues)
PcmParametersType = pydantic_to_strawberry_type(PcmParameters)
PcmControlModeType = pydantic_to_strawberry_type(PcmControlMode)
PcmControllerStateType = pydantic_to_strawberry_type(PcmControllerState)


PcmModule = ControlModule[
    PcmSensorValuesType,
    PcmControlValuesType,
    PcmParametersType,
    PcmControlModeType,
    PcmControllerStateType,
]


def resolve_module(
    module: PcmMessaging,
) -> PcmModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(
            PcmSensorValuesType, module.sensor_values
        ),
        control_values=optional_pydantic_to_graphql(
            PcmControlValuesType, module.control_values
        ),
        parameters=optional_pydantic_to_graphql(PcmParametersType, module.parameters),
        control_mode=SwitchingControlModeType.from_pydantic(
            PcmControlModeType, module.control_mode.mode
        )
        if module.control_mode
        else None,
        controller_state=optional_pydantic_to_graphql(
            PcmControllerStateType, module.controller_state
        ),
    )


def get_pcm_messaging(context):
    return context.pcm_messaging


@strawberry.type
@add_control_mutations("pcm", PcmControlValues, PcmControlValuesType, get_pcm_messaging)
@add_parameter_mutations("pcm", PcmParameters, PcmParametersType, get_pcm_messaging)
@add_automation_mode_mutation("pcm", get_pcm_messaging)
class PcmMutations:
    pass
