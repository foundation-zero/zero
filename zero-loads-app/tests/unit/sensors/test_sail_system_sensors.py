from abc import ABC
from typing import Annotated

from pydantic import Field

from loads.sensors.base import LoadsModel
from loads.sensors.units import Load, Position, RelativePosition


class SailSystemSensor(LoadsModel, ABC):
    TOPIC = "test-topic"

    load: Annotated[Load, Field(validation_alias="load")]
    position: Annotated[Position, Field(validation_alias="position")]
    relative_position: Annotated[
        RelativePosition, Field(validation_alias="relative_position")
    ]
    lock: Annotated[bool, Field(validation_alias="lock")]


def test_validate_message():
    message = {
        "load": 1500,
        "position": 2000,
        "relative_position": 500,
        "lock": True,
    }
    sensor = SailSystemSensor.model_validate(message)
    assert sensor.load == 15.0
    assert sensor.position == 2000
    assert sensor.relative_position == 0.5
    assert sensor.lock is True


class OverrideBoundsSensor(LoadsModel, ABC):
    TOPIC = "test-topic"

    override_load: Annotated[Load, Field(ge=-10, le=10)]


def test_override_constaints():
    assert (
        OverrideBoundsSensor.extract_minimum(
            OverrideBoundsSensor.model_fields["override_load"].metadata
        )
        == -10
    )
    assert (
        OverrideBoundsSensor.extract_maximum(
            OverrideBoundsSensor.model_fields["override_load"].metadata
        )
        == 10
    )


def test_validate_message_with_override_bounds():
    message = {
        "override_load": -500,
    }
    sensor = OverrideBoundsSensor.model_validate(message)
    assert sensor.override_load == -5.0
