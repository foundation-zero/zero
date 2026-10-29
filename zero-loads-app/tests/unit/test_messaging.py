from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from loads.api.messaging import Messaging
from loads.registry import ALARMS, VARIABLES, at_sensors
from loads.sensors.at import ApparentWindSpeed

MAX_MESSAGE_AGE = timedelta(seconds=30)
AWS_VARIABLE_ID = next(
    variable.id
    for variable in VARIABLES.values()
    if variable.topic == ApparentWindSpeed.TOPIC
)


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture()
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture()
def messaging(clock: FakeClock) -> Messaging:
    return Messaging(
        mqtt_client=MagicMock(),
        modules=[at_sensors],
        variable_definitions=VARIABLES,
        alarm_definitions=ALARMS,
        max_message_age=MAX_MESSAGE_AGE,
        clock=clock,
    )


async def receive_aws(messaging: Messaging, value: float):
    await messaging._receivers[ApparentWindSpeed.TOPIC].handle(
        ApparentWindSpeed.model_validate({"value": value})
    )


def test_value_is_none_before_any_message(messaging: Messaging):
    assert messaging.get_variable_value(AWS_VARIABLE_ID) is None


async def test_value_is_returned_within_max_age(
    messaging: Messaging, clock: FakeClock
):
    await receive_aws(messaging, 12.0)
    clock.now = MAX_MESSAGE_AGE.total_seconds()

    assert messaging.get_variable_value(AWS_VARIABLE_ID) == pytest.approx(12.0)


async def test_value_is_none_after_max_age(messaging: Messaging, clock: FakeClock):
    await receive_aws(messaging, 12.0)
    clock.now = MAX_MESSAGE_AGE.total_seconds() + 0.1

    assert messaging.get_variable_value(AWS_VARIABLE_ID) is None


async def test_new_message_restores_value(messaging: Messaging, clock: FakeClock):
    await receive_aws(messaging, 12.0)
    clock.now = 100.0
    await receive_aws(messaging, 14.0)

    assert messaging.get_variable_value(AWS_VARIABLE_ID) == pytest.approx(14.0)
