from typing import Annotated

from thrs.input_output.base import component_meta, ThrsModel
from thrs.input_output.model_builder import ModelBuilder
from thrs.input_output.definitions.sensor import FlowSensor


class SimpleSensors(ThrsModel):
    thrusters_flow_fwd: Annotated[FlowSensor, component_meta(yard_tag="50001057-22")]
    thrusters_flow_aft: Annotated[FlowSensor, component_meta(yard_tag="50001057-23")]


def test_builder():
    flow_message = """{
        "Flow": {
            "Value": 12.12,
            "HasValue": true,
            "IsValid": true,
            "TimeStamp": "2025-01-21T08:49:03.6735253Z"
        },
        "Temperature": {
            "Value": 17.12,
            "HasValue": true,
            "IsValid": true,
            "TimeStamp": "2025-01-21T08:49:03.6735253Z"
        }
    }"""
    flow_message_different = """{
        "Flow": {
            "Value": 14.12,
            "HasValue": true,
            "IsValid": true,
            "TimeStamp": "2025-01-21T08:49:03.6735253Z"
        },
        "Temperature": {
            "Value": 17.12,
            "HasValue": true,
            "IsValid": true,
            "TimeStamp": "2025-01-21T08:49:03.6735253Z"
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
