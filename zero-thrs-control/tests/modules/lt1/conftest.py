from datetime import datetime, timedelta
from pytest import fixture

from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary, HeatSource
from thrs.input_output.modules.lt1 import (
    Lt1SensorValues,
    Lt1SimulationInputs,
    Lt1SimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import lt1_path


@fixture
def simulation_inputs():
    return Lt1SimulationInputs(
        lt1_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(5000)),
        lt1_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(5000)),
        lt1_propdrive_aft1=HeatSource(heat_flow=Stamped.stamp(2800)),
        lt1_propdrive_aft2=HeatSource(heat_flow=Stamped.stamp(2800)),
        lt1_propdrive_fwd1=HeatSource(heat_flow=Stamped.stamp(1250)),
        lt1_propdrive_fwd2=HeatSource(heat_flow=Stamped.stamp(1250)),
        lt1_shorepower=HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        lt1_boilers_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(29)
        ),
    )


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        Lt1SensorValues,
        Lt1SimulationOutputs,
    )


@fixture
def executor(io_mapping, simulation_inputs):
    with Fmu(lt1_path) as fmu:
        yield SimulationExecutor(
            io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
        )
