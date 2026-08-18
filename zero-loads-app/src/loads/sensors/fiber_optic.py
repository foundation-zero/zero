from typing import Annotated

from pydantic import Field

from .base import LoadsModel
from .units import Load, VariableMeta


class FiberOptic(LoadsModel):
    TOPIC = "fiber-optic/values"
    main_v1_sb: Annotated[
        Load,
        VariableMeta(display_name="V1 SB", scale_min=0, scale_max=85),
        Field(validation_alias="mm-rigging-load-v1-stbd"),
    ]
    main_v1_ps: Annotated[
        Load,
        VariableMeta(display_name="V1 PT", scale_min=0, scale_max=85),
        Field(validation_alias="mm-rigging-load-v1-port"),
    ]
    main_d1_sb: Annotated[
        Load,
        VariableMeta(display_name="D1 SB", scale_min=0, scale_max=43),
        Field(validation_alias="mm-rigging-load-d1-stbd"),
    ]
    main_d1_ps: Annotated[
        Load,
        VariableMeta(display_name="D1 PT", scale_min=0, scale_max=43),
        Field(validation_alias="mm-rigging-load-d1-port"),
    ]
    mizzen_v1_sb: Annotated[
        Load,
        VariableMeta(display_name="V1 SB", scale_min=0, scale_max=47),
        Field(validation_alias="mz-rigging-load-v1-stbd"),
    ]
    mizzen_v1_ps: Annotated[
        Load,
        VariableMeta(display_name="V1 PT", scale_min=0, scale_max=47),
        Field(validation_alias="mz-rigging-load-v1-port"),
    ]
    mizzen_d1_sb: Annotated[
        Load,
        VariableMeta(display_name="D1 SB", scale_min=0, scale_max=25),
        Field(validation_alias="mz-rigging-load-d1-stbd"),
    ]
    mizzen_d1_ps: Annotated[
        Load,
        VariableMeta(display_name="D1 PT", scale_min=0, scale_max=25),
        Field(validation_alias="mz-rigging-load-d1-port"),
    ]
    mizzen_forestay: Annotated[
        Load,
        VariableMeta(display_name="Forestay", scale_min=0, scale_max=31),
    ] = 0
