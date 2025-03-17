from datetime import timedelta
from pathlib import Path

from pytest import fixture

from input_output.base import Stamped, ThrsModel
from input_output.fmu_mapping import build_inputs_for_fmu, build_outputs_from_fmu
from input_output.sensor import FlowSensor
from simulation.executor import Executor
from simulation.fmu import Fmu


class MiniModel(ThrsModel):
    flow_sensor: FlowSensor


class SecondMiniModel(ThrsModel):
    second_flow_sensor: FlowSensor


def test_fmu_inputs():

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


def test_fmu_roundtrip():
    control_values = MiniModel(
        flow_sensor=FlowSensor(
            flow=Stamped.stamp(12.12), temperature=Stamped.stamp(17.12)
        )
    )

    control_values = build_inputs_for_fmu(control_values)

    assert control_values, control_values == build_outputs_from_fmu(MiniModel, MiniModel, control_values, timedelta(seconds=1))  # type: ignore
