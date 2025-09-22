from pytest import fixture

from control.modules.thrusters import ThrustersControl, ThrustersParameters


@fixture
def thrusters_control() -> ThrustersControl:
    return ThrustersControl(
        ThrustersParameters()
    )
