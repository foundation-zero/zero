from typing import Annotated

from .base import LoadsModel
from .units import Load, VariableMeta


class FiberOptic(LoadsModel):
    TOPIC = "fiber-optic/placeholder"
    main_v1_sb: Annotated[Load, VariableMeta(display_name="V1 sb")]
    main_v1_ps: Annotated[Load, VariableMeta(display_name="V1 ps")]
    main_d1_sb: Annotated[Load, VariableMeta(display_name="D1 sb")]
    main_d1_ps: Annotated[Load, VariableMeta(display_name="D1 ps")]
    mizzen_v1_sb: Annotated[Load, VariableMeta(display_name="V1 sb")]
    mizzen_v1_ps: Annotated[Load, VariableMeta(display_name="V1 ps")]
    mizzen_d1_sb: Annotated[Load, VariableMeta(display_name="D1 sb")]
    mizzen_d1_ps: Annotated[Load, VariableMeta(display_name="D1 ps")]
    mizzen_forestay: Annotated[Load, VariableMeta(display_name="forestay")]
