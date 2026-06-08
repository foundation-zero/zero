from datetime import datetime, timedelta

from pytest import fixture

from thrs.control.modules.pcm import PcmControl, PcmParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary, TemperatureBoundary
from thrs.input_output.modules.pcm import (
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import pcm_path


@fixture
def control(executor):
    return PcmControl(PcmParameters(), executor.time)


@fixture
def simulation_inputs():
    return PcmSimulationInputs(
        pcm_producers_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(80)
        ),
        pcm_consumers_supply=TemperatureBoundary(temperature=Stamped.stamp(60)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
    )


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        PcmSensorValues,
        PcmSimulationOutputs,
    )


@fixture
def executor(io_mapping, simulation_inputs):
    with Fmu(pcm_path) as fmu:
        yield SimulationExecutor(
            io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
        )
