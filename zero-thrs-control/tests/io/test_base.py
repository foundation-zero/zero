from typing import Annotated, Generic, TypeVar
from pydantic import BaseModel, Field, ValidationError
import pytest
from input_output.base import Stamped, ThrsModel
from input_output.sensor import FlowSensor
from input_output.units import LMin


def test_flow_sensor():
    message = """{
        "flow": {
            "value": 12.12,
            "has-value": true,
            "is-valid": true,
            "timestamp": "2025-01-21T08:49:03.6735253Z"
        },
        "temperature": {
            "value": 17.12,
            "has-value": true,
            "is-valid": true,
            "timestamp": "2025-01-21T08:49:03.6735253Z"
        }
    }"""
    parsed_message = FlowSensor.model_validate_json(message)
    assert parsed_message.temperature.value == 17.12


def test_pydantic_generics():
    T = TypeVar("T")

    class A(BaseModel, Generic[T]):
        value: T

    assert A[int].model_fields["value"].metadata == []
    assert A[LMin].model_fields["value"].metadata != []
    assert A[Annotated[int, Field(ge=0)]].model_fields["value"].metadata == [
        Field(ge=0)
    ]


class MiniModel(ThrsModel):
    flow_sensor: FlowSensor


def test_values():

    assert {
        "flow_sensor__flow__l_min": 12.12,
        "flow_sensor__temperature__C": 17.12,
    } == MiniModel(
        flow_sensor=FlowSensor(
            flow=Stamped.stamp(12.12), temperature=Stamped.stamp(17.12)
        )
    ).values_for_fmu()


def test_fmu_roundtrip():
    value = MiniModel(
        flow_sensor=FlowSensor(
            flow=Stamped.stamp(12.12), temperature=Stamped.stamp(17.12)
        )
    )

    # abusing values_for_fmu to ignore the value timestamps
    assert (
        value.values_for_fmu()
        == MiniModel.build_from_fmu(value.values_for_fmu()).values_for_fmu()
    )
