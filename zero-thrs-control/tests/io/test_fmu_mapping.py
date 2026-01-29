from datetime import datetime
from typing import Annotated


from thrs.input_output.base import (
    SimulationInputs,
    Stamped,
    ThrsValues,
    component_meta,
    field_meta,
)
from thrs.input_output.definitions.units import Ratio
from thrs.input_output.fmu_mapping import (
    build_outputs_from_fmu,
    extract_non_fmu_values,
)
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.simulation.io_mapping import flatten_model_values


class MiniModel(ThrsValues):
    flow_sensor: FlowSensor


class SecondMiniModel(ThrsValues):
    second_flow_sensor: FlowSensor


class IncludedFieldComponent(ThrsValues):
    included_field: Annotated[Stamped[Ratio], field_meta(included_in_fmu=True)]


class ExcludedFieldComponent(ThrsValues):
    excluded_field: Annotated[Stamped[Ratio], field_meta(included_in_fmu=False)]
    included_field: Annotated[Stamped[Ratio], field_meta(included_in_fmu=True)]


class ExcludedSimulationInputs(SimulationInputs):
    excluded_component: Annotated[
        IncludedFieldComponent, component_meta(included_in_fmu=False)
    ]
    excluded_field_component: ExcludedFieldComponent


class ExcludedSensorValues(ThrsValues):
    excluded_component: Annotated[
        IncludedFieldComponent, field_meta(included_in_fmu=False)
    ]
    excluded_field_component: ExcludedFieldComponent


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


def test_fmu_input_ignore_excluded():
    value = Stamped.stamp(1.0)
    assert {
        "excluded_field_component__included_field__ratio": 1.0
    } == flatten_model_values(
        ExcludedSimulationInputs(
            excluded_component=IncludedFieldComponent(
                included_field=Stamped.stamp(1.0)
            ),
            excluded_field_component=ExcludedFieldComponent(
                excluded_field=value, included_field=value
            ),
        ),
        fmu_only=True,
    )


def test_extract_excluded():
    value = Stamped.stamp(1.0)
    assert {
        "excluded_component": {
            "included_field": value,
        },
        "excluded_field_component": {
            "excluded_field": value,
        },
    } == extract_non_fmu_values(
        ExcludedSimulationInputs(
            excluded_component=IncludedFieldComponent(included_field=value),
            excluded_field_component=ExcludedFieldComponent(
                excluded_field=value, included_field=value
            ),
        ),
        ExcludedSensorValues,
    )


def test_fmu_roundtrip():
    time = datetime.now()
    control_values = MiniModel(
        flow_sensor=FlowSensor(
            flow=Stamped(value=12.12, timestamp=time),
            temperature=Stamped(value=17.12, timestamp=time),
        )
    )

    values = flatten_model_values(control_values, fmu_only=True)

    assert values, values == build_outputs_from_fmu((MiniModel,), values, time)
