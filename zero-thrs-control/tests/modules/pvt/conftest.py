from datetime import datetime, timedelta

from pytest import fixture

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.pvt import PvtControl, PvtParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    TemperatureBoundary,
)
from thrs.input_output.modules.pvt import (
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import pvt_path


@fixture
def simulation_inputs():
    return PvtSimulationInputs(
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(8000)),
        pvt_pcm_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
    )


@fixture
def control(simulation):
    return PvtControl(
        PvtParameters(), simulation.time, MachineStateLoggingServiceNoop()
    )


@fixture
def simulation(simulation_inputs):
    with Fmu(pvt_path) as fmu:
        yield Simulation(
            PvtSensorValues,
            PvtSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )
