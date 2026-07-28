from datetime import datetime
from typing import Annotated

from pydantic import computed_field

from thrs.input_output.base import (
    SimulationInputs,
    Stamped,
    ThrsValues,
    component_meta,
    computed_meta,
    field_meta,
)
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.definitions.units import Ratio
from thrs.input_output.fmu_mapping import (
    build_fmu_key_mapping,
    build_outputs_from_fmu,
    extract_non_fmu_values,
)
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


class ModelWithComputed(ThrsValues):
    flow_sensor: FlowSensor

    @computed_field(
        json_schema_extra=computed_meta(
            component_type="flow_sensor", included_in_fmu=True
        )
    )
    @property
    def computed_component(self) -> FlowSensor:
        return self.flow_sensor


def test_fmu_simple_inputs():
    mini_model = MiniModel(
        flow_sensor=FlowSensor(
            flow=Stamped.stamp(12.12), temperature=Stamped.stamp(17.12)
        )
    )

    assert {
        "flow_sensor__flow__l_min": 12.12,
        "flow_sensor__temperature__C": 17.12,
    } == flatten_model_values(mini_model, build_fmu_key_mapping(MiniModel))

    second_mini_model = SecondMiniModel(
        second_flow_sensor=FlowSensor(
            flow=Stamped.stamp(2), temperature=Stamped.stamp(3)
        )
    )
    assert {
        "second_flow_sensor__flow__l_min": 2,
        "second_flow_sensor__temperature__C": 3,
    } == flatten_model_values(second_mini_model, build_fmu_key_mapping(SecondMiniModel))


def test_fmu_input_ignore_excluded():
    value = Stamped.stamp(1.0)
    excluded_simulation_inputs = ExcludedSimulationInputs(
        excluded_component=IncludedFieldComponent(included_field=Stamped.stamp(1.0)),
        excluded_field_component=ExcludedFieldComponent(
            excluded_field=value, included_field=value
        ),
    )

    assert {
        "excluded_field_component__included_field__ratio": 1.0
    } == flatten_model_values(
        excluded_simulation_inputs,
        build_fmu_key_mapping(ExcludedSimulationInputs),
    )


def test_fmu_computed_field():
    model = ModelWithComputed(
        flow_sensor=FlowSensor(
            flow=Stamped.stamp(12.12), temperature=Stamped.stamp(17.12)
        )
    )

    assert {
        "flow_sensor__flow__l_min": 12.12,
        "flow_sensor__temperature__C": 17.12,
        "computed_component__flow__l_min": 12.12,
        "computed_component__temperature__C": 17.12,
    } == flatten_model_values(model, build_fmu_key_mapping(ModelWithComputed))


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

    values = flatten_model_values(
        control_values, build_fmu_key_mapping(MiniModel, fmu_only=True)
    )

    assert values, values == build_outputs_from_fmu((MiniModel,), values, time)
