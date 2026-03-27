from datetime import datetime, timedelta
from pytest import fixture

from thrs.control.modules.lt2 import Lt2Alarms, Lt2Control, Lt2Parameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary, HeatSource
from thrs.input_output.modules.lt2 import (
    Lt2SensorValues,
    Lt2SimulationInputs,
    Lt2SimulationOutputs,
)
from thrs.orchestration.cycler import Cycler
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import lt2_path


@fixture
def simulation_inputs():
    return Lt2SimulationInputs(
        lt2_brightloop_fwd1=HeatSource(heat_flow=Stamped.stamp(500)),
        lt2_brightloop_fwd2=HeatSource(heat_flow=Stamped.stamp(500)),
        lt2_ugrid1=HeatSource(heat_flow=Stamped.stamp(2000)),
        lt2_ugrid2=HeatSource(heat_flow=Stamped.stamp(2000)),
        lt2_brightloop_aft1=HeatSource(heat_flow=Stamped.stamp(500)),
        lt2_brightloop_aft2=HeatSource(heat_flow=Stamped.stamp(500)),
        lt2_brightloop_aft3=HeatSource(heat_flow=Stamped.stamp(500)),
        lt2_brightloop_aft4=HeatSource(heat_flow=Stamped.stamp(500)),
        lt2_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        lt2_boilers_supply=Boundary(
            temperature=Stamped.stamp(35), flow=Stamped.stamp(20)
        ),
    )


@fixture()
def control(executor) -> Lt2Control:
    return Lt2Control(Lt2Parameters(), executor.time)


@fixture
def alarms() -> Lt2Alarms:
    return Lt2Alarms()


@fixture()
def cycler(control, executor, alarms) -> Cycler:
    return Cycler(control, executor, alarms)


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        Lt2SensorValues,
        Lt2SimulationOutputs,
    )


@fixture
def executor(io_mapping, simulation_inputs):
    with Fmu(lt2_path) as fmu:
        yield SimulationExecutor(
            io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
        )
