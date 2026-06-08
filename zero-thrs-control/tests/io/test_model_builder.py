from typing import Annotated

from tests.orchestration.simples import SimpleInOut
from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.model_builder import CombinedModelBuilder, PartialModelBuilder


class SimpleSensors(ThrsValues):
    thrusters_flow_fwd: Annotated[FlowSensor, component_meta(yard_tag="50001057-22")]
    thrusters_flow_aft: Annotated[FlowSensor, component_meta(yard_tag="50001057-23")]


def test_partial_model_builder():
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

    builder = PartialModelBuilder(SimpleSensors)
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


def test_combined_model_builder():
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

    builder = CombinedModelBuilder({"module1": SimpleInOut})
    builder.input("module1/go-with-the", flow_message)
    result = builder.result()
    assert result is not None
    module1 = result.values["module1"]
    assert isinstance(module1, SimpleInOut)
    assert module1.go_with_the.flow.value == 12.12
