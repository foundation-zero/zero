from pydantic import Field

from .base import LoadsModelBytes


class SystemLatitude(LoadsModelBytes):
    TOPIC = "atpx/4352/3840"
    load: float


class SystemLongitude(LoadsModelBytes):
    TOPIC = "atpx/4353/3840"
    load: int = Field()


class UTCDate(LoadsModelBytes):
    TOPIC = "atpx/256/3840"
    # FIXME - only float and int are supported. See generator/gen.py
    load: float = Field()


class SystemBoatSpeedKts(LoadsModelBytes):
    TOPIC = "atpx/4610/3840"
    load: float = Field()


class CurrentDirectionT(LoadsModelBytes):
    TOPIC = "atpx/4656/3840"


class CurrentSpeedKts(LoadsModelBytes):
    TOPIC = "atpx/4658/3840"


class VMGtoWindKts(LoadsModelBytes):
    TOPIC = "atpx/4885/3840"


class Leeway(LoadsModelBytes):
    TOPIC = "atpx/4936/3840"


class SystemDepthM(LoadsModelBytes):
    TOPIC = "atpx/5121/3840"


class SystemDepthSourceIndex(LoadsModelBytes):
    TOPIC = "atpx/5124/3840"


class SystemHeadingT(LoadsModelBytes):
    TOPIC = "atpx/5376/3840"


...
