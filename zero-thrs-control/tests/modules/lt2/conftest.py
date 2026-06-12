from datetime import datetime, timedelta

from pytest import fixture

from thrs.control.modules.lt2 import Lt2Alarms, Lt2Control, Lt2Parameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary, Converter
from thrs.input_output.modules.lt2 import (
    Lt2SensorValues,
    Lt2SimulationInputs,
    Lt2SimulationOutputs,
)
from thrs.orchestration.runner import Runner
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import lt2_path

SEAWATER_TEMPERATURE = 20


@fixture
def simulation_inputs_inactive():
    return Lt2SimulationInputs(
        lt2_brightloop_fwd1=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt2_brightloop_fwd2=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt2_ugrid1=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        lt2_ugrid2=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        lt2_brightloop_aft1=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt2_brightloop_aft2=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt2_brightloop_aft3=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt2_brightloop_aft4=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt2_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        lt2_boilers_supply=Boundary(
            temperature=Stamped.stamp(35), flow=Stamped.stamp(20)
        ),
    )


@fixture
def simulation_inputs_brightloops_aft_active():
    return Lt2SimulationInputs(
        lt2_brightloop_fwd1=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt2_brightloop_fwd2=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt2_ugrid1=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        lt2_ugrid2=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        lt2_brightloop_aft1=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_brightloop_aft2=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_brightloop_aft3=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_brightloop_aft4=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        lt2_boilers_supply=Boundary(
            temperature=Stamped.stamp(35), flow=Stamped.stamp(20)
        ),
    )


@fixture
def simulation_inputs():
    return Lt2SimulationInputs(
        lt2_brightloop_fwd1=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_brightloop_fwd2=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_ugrid1=Converter(heat_flow=Stamped.stamp(2000), active=Stamped.stamp(True)),
        lt2_ugrid2=Converter(heat_flow=Stamped.stamp(2000), active=Stamped.stamp(True)),
        lt2_brightloop_aft1=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_brightloop_aft2=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_brightloop_aft3=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_brightloop_aft4=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        lt2_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        lt2_boilers_supply=Boundary(
            temperature=Stamped.stamp(35), flow=Stamped.stamp(20)
        ),
    )


@fixture()
def control(simulation) -> Lt2Control:
    return Lt2Control(Lt2Parameters(), simulation.time)


@fixture
def alarms() -> Lt2Alarms:
    return Lt2Alarms()


@fixture()
def runner(control: Lt2Control, simulation, alarms: Lt2Alarms) -> Runner:
    simulation.transceive = simulation.tick  # type: ignore # TODO: Make this make sense
    return Runner(simulation, control, alarms)


@fixture
def simulation(simulation_inputs):
    with Fmu(lt2_path) as fmu:
        yield Simulation(
            Lt2SensorValues,
            Lt2SimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )
