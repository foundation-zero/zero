from typing import Annotated

from input_output.base import Meta, ThrsModel
from input_output.model_builder import ModelBuilder
from input_output.definitions.sensor import FlowSensor


class SimpleSensors(ThrsModel):
    thrusters_flow_fwd: Annotated[FlowSensor, Meta("50001057-22")]
    thrusters_flow_aft: Annotated[FlowSensor, Meta("50001057-23")]


def test_builder():
    flow_message = """{
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
    flow_message_different = """{
        "flow": {
            "value": 14.12,
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

    builder = ModelBuilder(SimpleSensors)
    builder.input("thrusters_flow_fwd", flow_message)
    assert builder.result() is None
    builder.input("thrusters_flow_aft", flow_message)
    result = builder.result()
    assert result is not None
    assert result.thrusters_flow_aft.flow.value == 12.12
    builder.input("thrusters_flow_fwd", flow_message_different)
    result = builder.result()
    assert result is not None
    assert result.thrusters_flow_fwd.flow.value == 14.12
    assert result.thrusters_flow_aft.flow.value == 12.12
