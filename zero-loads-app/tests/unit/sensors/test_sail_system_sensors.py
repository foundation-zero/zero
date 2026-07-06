from abc import ABC
from typing import Annotated

from pydantic import Field
from pytest import fixture

from loads.registry.registry import (
    _build_loads_model_variable_definitions,
    _build_sail_system_alarm_definitions,
)
from loads.sensors.base import LoadsModel
from loads.sensors.sail_system import (
    Load,
    LoadAlarm,
    MaxLoad,
    RelativePosition,
)


@fixture
def message():
    return {
        "load": 1500,
        "relative_position": 500,
        "lock": True,
        "load_alarm": True,
        "max_load": 10000,
    }


class SailSystemSensor(LoadsModel, ABC):
    TOPIC = "test-topic"

    load: Annotated[Load, Field(validation_alias="load")]
    relative_position: Annotated[
        RelativePosition, Field(validation_alias="relative_position")
    ]
    lock: Annotated[bool, Field(validation_alias="lock")]
    load_alarm: Annotated[LoadAlarm, Field(validation_alias="load_alarm")]
    max_load: Annotated[MaxLoad, Field(validation_alias="max_load")]


def test_validate_message(message):
    sensor = SailSystemSensor.model_validate(message)
    assert sensor.load == 15.0
    assert sensor.relative_position == 0.5
    assert sensor.lock is True
    assert sensor.load_alarm is True
    assert sensor.max_load == 100.0


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


def test_build_alarm_defintitions(message):
    sensor = SailSystemSensor.model_validate(message)
    variable_definitions = _build_loads_model_variable_definitions(SailSystemSensor)
    alarm_definitions = _build_sail_system_alarm_definitions(
        SailSystemSensor,
        variable_definitions,
    )

    assert len(alarm_definitions) == 1

    alarm = alarm_definitions[0]
    assert alarm.id == "sail-system-sensor-load-alarm"
    assert alarm.actual_definition.id == "sail-system-sensor-load"
    assert alarm.get_active(sensor) is True
    assert alarm.get_actual(sensor) == 15.0
    assert alarm.get_threshold(sensor) == 100.0
