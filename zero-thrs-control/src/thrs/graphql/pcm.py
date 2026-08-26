import strawberry

from thrs.control.modules.pcm import PcmControllerState, PcmControlMode, PcmParameters
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
from thrs.input_output.modules.pcm import PcmControlValues, PcmSensorValues

PcmSensorValuesType = pydantic_to_strawberry_type(
    PcmSensorValues, include_computed=True
)
PcmControlValuesType = pydantic_to_strawberry_type(PcmControlValues)
PcmParametersType = pydantic_to_strawberry_type(PcmParameters)
PcmControlModeType = pydantic_to_strawberry_type(PcmControlMode)
PcmControllerStateType = empty_pydantic_type_to_strawberry_type(PcmControllerState)

PcmModule = ControlModule[
    PcmSensorValuesType,
    PcmControlValuesType,
    PcmParametersType,
    PcmControlModeType,
    PcmControllerStateType,
]


def get_pcm_messaging(context):
    return context.pcm_messaging


@strawberry.type
@add_control_mutations("pcm", PcmControlValues, PcmControlValuesType, get_pcm_messaging)
@add_parameter_mutations("pcm", PcmParameters, PcmParametersType, get_pcm_messaging)
@add_automation_mode_mutation("pcm", get_pcm_messaging)
class PcmMutations:
    pass
