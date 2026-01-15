from .base import LoadsBytesModel


class ApparentWindSpeed(LoadsBytesModel):
    TOPIC = "atpx/4864/3840"
    value: float


class ApparentWindAngle(LoadsBytesModel):
    TOPIC = "atpx/4865/3840"
    value: float
