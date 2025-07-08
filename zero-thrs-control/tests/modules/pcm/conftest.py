from datetime import datetime, timedelta
from pytest import fixture

from control.modules.pcm import PcmControl, PcmParameters
from input_output.base import Stamped
from input_output.definitions.simulation import Boundary, TemperatureBoundary
from input_output.modules.pcm import PcmSensorValues, PcmSimulationInputs, PcmSimulationOutputs
from orchestration.executor import SimulationExecutor
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping
from simulation.models.fmu_paths import pcm_path


@fixture
def control():
    return PcmControl(PcmParameters())


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
    with Fmu(pcm_path) as fmu:
        yield IoMapping(
            fmu,
            PcmSensorValues,
            PcmSimulationOutputs,
        )

@fixture
def executor(io_mapping, simulation_inputs):
    return SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=1)
    )
