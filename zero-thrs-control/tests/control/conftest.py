from datetime import datetime
from pytest import fixture

from thrs.control.modules.thrusters import ThrustersControl, ThrustersParameters


@fixture
def thrusters_control() -> ThrustersControl:
    return ThrustersControl(
        ThrustersParameters(), datetime.now()
    )
