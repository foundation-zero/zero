from datetime import datetime
from typing import Annotated


from thrs.input_output.base import Stamped, ThrsModel, component_meta, field_meta
from thrs.input_output.definitions.units import Ratio
from thrs.input_output.fmu_mapping import (
    build_outputs_from_fmu,
    extract_non_fmu_values,
)
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.simulation.io_mapping import flatten_model_values


class MiniModel(ThrsModel):
    flow_sensor: FlowSensor


class SecondMiniModel(ThrsModel):
    second_flow_sensor: FlowSensor


class ExcludedInputComponent(ThrsModel):
    excluded_field: Annotated[Stamped[Ratio], field_meta(included_in_fmu=False)]


class ExcludedInputModel(ThrsModel):
    excluded_component: ExcludedInputComponent


class ExcludedSensor(ThrsModel):
    excluded_field: Stamped[Ratio]


class ExcludedSensorValues(ThrsModel):
    excluded_component: Annotated[
        ExcludedSensor, component_meta(yard_tag="", included_in_fmu=False)
    ]


def test_fmu_simple_inputs():
    assert {
        "flow_sensor__flow__l_min": 12.12,
        "flow_sensor__temperature__C": 17.12,
    } == flatten_model_values(
        MiniModel(
            flow_sensor=FlowSensor(
                flow=Stamped.stamp(12.12), temperature=Stamped.stamp(17.12)
            )
        ),
        fmu_only=True,
    )
    assert {
        "second_flow_sensor__flow__l_min": 2,
        "second_flow_sensor__temperature__C": 3,
    } == flatten_model_values(
        SecondMiniModel(
            second_flow_sensor=FlowSensor(
                flow=Stamped.stamp(2), temperature=Stamped.stamp(3)
            )
        ),
        fmu_only=True,
    )


def test_fmu_input_ignore_extras():
    assert {} == flatten_model_values(
        ExcludedInputModel(
            excluded_component=ExcludedInputComponent(excluded_field=Stamped.stamp(1.0))
        ),
        fmu_only=True,
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

    values = flatten_model_values(values, fmu_only=True)

    assert values, values == build_outputs_from_fmu((MiniModel,), values, time)
