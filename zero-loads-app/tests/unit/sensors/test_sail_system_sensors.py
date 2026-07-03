from abc import ABC
from typing import Annotated

from pydantic import Field

from loads.sensors.base import LoadsModel
from loads.sensors.sail_system import (
    Load,
    MaxLoad,
    Position,
    RelativePosition,
)


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


def test_load_bounds():
    message = {"load": 1000, "override_load": -500}

    class OverrideLoadSensor(LoadsModel, ABC):
        override_load: Annotated[
            Load, Field(ge=-10, le=10, validation_alias="override_load")
        ]
        load: Annotated[Load, Field(validation_alias="load", ge=0, le=20)]

    sensor = OverrideLoadSensor.model_validate(message)

    assert (
        OverrideLoadSensor.extract_minimum(
            OverrideLoadSensor.model_fields["override_load"].metadata
        )
        == -10
    )
    assert (
        OverrideLoadSensor.extract_maximum(
            OverrideLoadSensor.model_fields["override_load"].metadata
        )
        == 10
    )
    assert (
        OverrideLoadSensor.extract_minimum(
            OverrideLoadSensor.model_fields["load"].metadata
        )
        == 0
    )
    assert (
        OverrideLoadSensor.extract_maximum(
            OverrideLoadSensor.model_fields["load"].metadata
        )
        == 20
    )
    assert sensor.override_load == -5.0
    assert sensor.load == 10.0


def test_nested_alias_uses_strictest_bounds():
    class OverrideMaxLoadSensor(LoadsModel, ABC):
        max_load: Annotated[
            MaxLoad,
            Field(ge=0, le=8, validation_alias="max_load"),
        ]

    assert (
        OverrideMaxLoadSensor.extract_minimum(
            OverrideMaxLoadSensor.model_fields["max_load"].metadata
        )
        == 0
    )
    assert (
        OverrideMaxLoadSensor.extract_maximum(
            OverrideMaxLoadSensor.model_fields["max_load"].metadata
        )
        == 8
    )
