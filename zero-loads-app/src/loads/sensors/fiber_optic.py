from typing import Annotated

from .base import LoadsModel
from .units import Load, VariableMeta


class FiberOptic(LoadsModel):
    TOPIC = "fiber-optic/placeholder"
    main_v1_sb: Annotated[
        Load, VariableMeta(display_name="V1 SB", scale_min=0, scale_max=85)
    ]
    main_v1_ps: Annotated[
        Load, VariableMeta(display_name="V1 PT", scale_min=0, scale_max=85)
    ]
    main_d1_sb: Annotated[
        Load, VariableMeta(display_name="D1 SB", scale_min=0, scale_max=43)
    ]
    main_d1_ps: Annotated[
        Load, VariableMeta(display_name="D1 PT", scale_min=0, scale_max=43)
    ]
    mizzen_v1_sb: Annotated[
        Load, VariableMeta(display_name="V1 SB", scale_min=0, scale_max=47)
    ]
    mizzen_v1_ps: Annotated[
        Load, VariableMeta(display_name="V1 PT", scale_min=0, scale_max=47)
    ]
    mizzen_d1_sb: Annotated[
        Load, VariableMeta(display_name="D1 SB", scale_min=0, scale_max=25)
    ]
    mizzen_d1_ps: Annotated[
        Load, VariableMeta(display_name="D1 PT", scale_min=0, scale_max=25)
    ]
    mizzen_forestay: Annotated[
        Load, VariableMeta(display_name="Forestay", scale_min=0, scale_max=31)
    ]
