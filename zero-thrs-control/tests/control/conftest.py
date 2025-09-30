from datetime import datetime, timedelta
from pytest import fixture

from thrs.control.modules.thrusters import ThrustersControl, ThrustersParameters


class TestTime:
    def __init__(self, duration: timedelta = timedelta(seconds=1)):
        self._time = datetime.now()
        self._duration = duration

    def time(self) -> datetime:
        self._time += self._duration
        return self._time


@fixture
def thrusters_control(test_time) -> ThrustersControl:
    return ThrustersControl(ThrustersParameters(), test_time.time)


@fixture()
def test_time() -> TestTime:
    return TestTime()
