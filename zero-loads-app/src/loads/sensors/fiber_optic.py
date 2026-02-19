from .base import LoadsModel
from .units import Load


class SideStayMeasurements(LoadsModel):
    TOPIC = "fiber-optic/side-stay-measurements"

    v1: Load
    d1: Load
    d2: Load
    d3: Load
    d4: Load
    d5: Load
