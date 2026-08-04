import strawberry

from thrs.control.modules.converters import ConvertersControlMode
from thrs.control.modules.dc import DcControllerState, DcControlMode, DcParameters
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
from thrs.input_output.modules.dc import DcControlValues, DcSensorValues

DcSensorValuesType = pydantic_to_strawberry_type(DcSensorValues, include_computed=True)
DcControlValuesType = pydantic_to_strawberry_type(DcControlValues)
DcParametersType = pydantic_to_strawberry_type(DcParameters)
ConvertersControlModeType = pydantic_to_strawberry_type(ConvertersControlMode)
DcControlModeType = pydantic_to_strawberry_type(DcControlMode)
DcControllerStateType = empty_pydantic_type_to_strawberry_type(DcControllerState)


DcModule = ControlModule[
    DcSensorValuesType,
    DcControlValuesType,
    DcParametersType,
    DcControlModeType,
    DcControllerStateType,
]


def get_dc_messaging(context):
    return context.dc_messaging


@strawberry.type
@add_control_mutations(
    "dc",
    DcControlValues,
    DcControlValuesType,
    get_dc_messaging,
)
@add_parameter_mutations("dc", DcParameters, DcParametersType, get_dc_messaging)
@add_automation_mode_mutation("dc", get_dc_messaging)
class DcMutations:
    pass
