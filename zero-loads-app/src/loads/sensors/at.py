from typing import Annotated

from .base import LoadsBytesModel
from .units import Angle, Speed, VariableMeta


class ApparentWindSpeed(LoadsBytesModel):
    TOPIC = "atpx/4864/3840"
    value: Annotated[Speed, VariableMeta(name="aws")]


class ApparentWindAngle(LoadsBytesModel):
    TOPIC = "atpx/4865/3840"
    value: Annotated[Angle, VariableMeta(name="awa")]
