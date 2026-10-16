from abc import ABC
from typing import Annotated

from pydantic import Field
from pytest import fixture, raises

from loads.registry.registry import (
    _build_loads_model_variable_definitions,
    _build_sail_system_alarm_definitions,
)
from loads.sensors.base import LoadsModel
from loads.sensors.sail_system import (
    Load,
    LoadAlarm,
    MaxLoad,
    MaxPosition,
    MaxPositionAlarm,
    Position,
    RelativePosition,
)
from loads.sensors.units import VariableMeta


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
    assert alarm.id == "sail-system-sensor-max-load-alarm"
    assert alarm.actual_definition.id == "sail-system-sensor-load"
    assert alarm.get_active(sensor) is True
    assert alarm.get_actual(sensor) == 15.0
    assert alarm.get_threshold(sensor) == 100.0
    assert alarm.unit == "tonne"


def test_technical_name_overrides_derived_variable_id(message):
    class TechnicalNameSensor(LoadsModel, ABC):
        TOPIC = "test-topic"

        load: Annotated[
            Load,
            Field(validation_alias="load"),
            VariableMeta(technical_name="renamed-load"),
        ]
        load_alarm: Annotated[LoadAlarm, Field(validation_alias="load_alarm")]
        max_load: Annotated[MaxLoad, Field(validation_alias="max_load")]

    sensor = TechnicalNameSensor.model_validate(message)
    variable_definitions = _build_loads_model_variable_definitions(TechnicalNameSensor)
    alarm_definitions = _build_sail_system_alarm_definitions(
        TechnicalNameSensor,
        variable_definitions,
    )

    assert [variable.id for variable in variable_definitions] == ["renamed-load"]
    assert alarm_definitions[0].id == "technical-name-sensor-max-load-alarm"
    assert alarm_definitions[0].actual_definition.id == "renamed-load"
    assert alarm_definitions[0].get_actual(sensor) == 15.0


class PositionSensor(LoadsModel, ABC):
    TOPIC = "test-topic"

    relative_position: RelativePosition
    position: Position
    max_position_alarm: MaxPositionAlarm
    max_position: MaxPosition


def test_position_alarm_reports_the_position_in_mm():
    sensor = PositionSensor.model_validate(
        {
            "st_position/i_Position_permille": 1000,
            "st_position/i_Position_mm": 335,
            "st_position/x_MaxLimitReached": True,
            "st_position/i_MaxPosition": 330,
        }
    )
    variable_definitions = _build_loads_model_variable_definitions(PositionSensor)
    [alarm] = _build_sail_system_alarm_definitions(PositionSensor, variable_definitions)

    assert alarm.actual_definition.id == "position-sensor-relative-position"
    assert alarm.unit == "mm"
    assert alarm.get_actual(sensor) == 335
    assert alarm.get_threshold(sensor) == 330


def test_alarm_value_from_requires_a_field_with_a_unit():
    class MissingPositionSensor(LoadsModel, ABC):
        TOPIC = "test-topic"

        relative_position: RelativePosition
        max_position_alarm: MaxPositionAlarm

    variable_definitions = _build_loads_model_variable_definitions(
        MissingPositionSensor
    )

    with raises(ValueError, match="takes its value from 'position'"):
        _build_sail_system_alarm_definitions(
            MissingPositionSensor, variable_definitions
        )
