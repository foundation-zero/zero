from typing import Annotated

from thrs.input_output.base import ThrsValues, component_meta
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.input_output.model_builder import PartialModelBuilder


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


def _flow_message(flow: float) -> str:
    return f"""{{
        "Flow": {{"Value": {flow}, "TimeStamp": "2025-01-21T08:49:03.6735253Z"}},
        "Temperature": {{"Value": 17.12, "TimeStamp": "2025-01-21T08:49:03.6735253Z"}}
    }}"""


def test_partial_model_builder_calls_on_complete_once():
    builder = PartialModelBuilder(SimpleSensors)
    completed: list[SimpleSensors] = []
    builder.on_complete(completed.append)

    builder.input("thrusters_flow_fwd", _flow_message(12.0))
    assert completed == []

    builder.input("thrusters_flow_aft", _flow_message(12.0))
    first = builder.result()
    assert first is not None
    assert completed == [first]
    assert completed[0].thrusters_flow_fwd is not first.thrusters_flow_fwd

    builder.input("thrusters_flow_fwd", _flow_message(14.0))
    assert completed == [first]

    late: list[SimpleSensors] = []
    builder.on_complete(late.append)
    assert late == [builder.result()]
