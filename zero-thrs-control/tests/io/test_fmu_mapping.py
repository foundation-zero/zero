from datetime import datetime
from typing import Annotated


from input_output.base import FieldMeta, Meta, Stamped, ThrsModel
from input_output.definitions.units import Ratio
from input_output.fmu_mapping import build_inputs_for_fmu, build_outputs_from_fmu, extract_non_fmu_values
from input_output.definitions.sensor import FlowSensor


class MiniModel(ThrsModel):
    flow_sensor: FlowSensor


class SecondMiniModel(ThrsModel):
    second_flow_sensor: FlowSensor


class ExcludedInputComponent(ThrsModel):
    excluded_field: Annotated[Stamped[Ratio], FieldMeta(included_in_fmu=False)]


class ExcludedInputModel(ThrsModel):
    excluded_component: ExcludedInputComponent


class ExcludedSensor(ThrsModel):
    excluded_field: Stamped[Ratio]


class ExcludedSensorValues(ThrsModel):
    excluded_component: Annotated[ExcludedSensor, Meta("", included_in_fmu=False)]


def test_fmu_simple_inputs():
    assert {
        "flow_sensor__flow__l_min": 12.12,
        "flow_sensor__temperature__C": 17.12,
    } == build_inputs_for_fmu(
        MiniModel(
            flow_sensor=FlowSensor(
                flow=Stamped.stamp(12.12), temperature=Stamped.stamp(17.12)
            )
        ),
    )
    assert {
        "second_flow_sensor__flow__l_min": 2,
        "second_flow_sensor__temperature__C": 3,
    } == build_inputs_for_fmu(
        SecondMiniModel(
            second_flow_sensor=FlowSensor(
                flow=Stamped.stamp(2), temperature=Stamped.stamp(3)
            )
        )
    )


def test_fmu_input_ignore_extras():
    assert {} == build_inputs_for_fmu(
        ExcludedInputModel(
            excluded_component=ExcludedInputComponent(excluded_field=Stamped.stamp(1.0))
        )
    )


def test_extract_non_fmu_values():
    value = Stamped.stamp(1.0)
    assert {
        "excluded_component": {
            "excluded_field": value,
        }
    } == extract_non_fmu_values(
        ExcludedInputModel(
            excluded_component=ExcludedInputComponent(excluded_field=value)
        ),
        ExcludedSensorValues,
    )


def test_fmu_roundtrip():
    time = datetime.now()
    values = MiniModel(
        flow_sensor=FlowSensor(
            flow=Stamped(value=12.12, timestamp=time),
            temperature=Stamped(value=17.12, timestamp=time),
        )
    )

    values = build_inputs_for_fmu(values)

    assert values, values == build_outputs_from_fmu([MiniModel], values, time)
