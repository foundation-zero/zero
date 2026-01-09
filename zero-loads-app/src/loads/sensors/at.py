from .base import LoadsBytesModel


class SystemLatitude(LoadsBytesModel):
    TOPIC = "atpx/4352/3840"
    value: float


class SystemLongitude(LoadsBytesModel):
    TOPIC = "atpx/4353/3840"
    value: int


class UTCDate(LoadsBytesModel):
    TOPIC = "atpx/256/3840"
    # FIXME - only float and int are supported. See generator/gen.py
    value: float


class SystemBoatSpeedKts(LoadsBytesModel):
    TOPIC = "atpx/4610/3840"
    value: float


class CurrentDirectionT(LoadsBytesModel):
    TOPIC = "atpx/4656/3840"


class CurrentSpeedKts(LoadsBytesModel):
    TOPIC = "atpx/4658/3840"


class VMGtoWindKts(LoadsBytesModel):
    TOPIC = "atpx/4885/3840"


class Leeway(LoadsBytesModel):
    TOPIC = "atpx/4936/3840"


class SystemDepthM(LoadsBytesModel):
    TOPIC = "atpx/5121/3840"


class SystemDepthSourceIndex(LoadsBytesModel):
    TOPIC = "atpx/5124/3840"


class SystemHeadingT(LoadsBytesModel):
    TOPIC = "atpx/5376/3840"


...
