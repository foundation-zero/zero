from typing import Annotated

from pydantic import Field

from .base import LoadsModel
from .units import Angle, Speed, VariableMeta


class ApparentWindSpeed(LoadsModel):
    TOPIC = "atpx/processed/app_wind_speed_kts/atprocessor_0"
    value: Annotated[
        Speed,
        VariableMeta(name="aws", type="actual"),
        Field(validation_alias="value"),
    ]


class ApparentWindAngle(LoadsModel):
    TOPIC = "atpx/processed/app_wind_angle/atprocessor_0"
    value: Annotated[
        Angle,
        VariableMeta(name="awa", type="actual"),
        Field(validation_alias="value"),
    ]
