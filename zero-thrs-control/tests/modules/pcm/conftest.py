from datetime import datetime, timedelta

from pytest import fixture

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.pcm import PcmControl, PcmParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary, TemperatureBoundary
from thrs.input_output.modules.pcm import (
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import pcm_path


@fixture
def control(simulation):
    return PcmControl(
        PcmParameters(), simulation.time, MachineStateLoggingServiceNoop()
    )


@fixture
def simulation_inputs():
    return PcmSimulationInputs(
        pcm_thrusters_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(40)
        ),
        pcm_consumers_supply=TemperatureBoundary(temperature=Stamped.stamp(60)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
        pcm_pvt_supply=Boundary(temperature=Stamped.stamp(70), flow=Stamped.stamp(70)),
    )


@fixture
def simulation(simulation_inputs):
    with Fmu(pcm_path) as fmu:
        yield Simulation(
            PcmSensorValues,
            PcmSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )
