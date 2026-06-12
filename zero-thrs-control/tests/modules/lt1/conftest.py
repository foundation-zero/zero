from datetime import datetime, timedelta

from pytest import fixture

from thrs.control.modules.lt1 import Lt1Alarms, Lt1Control, Lt1Parameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    Converter,
    HeatSource,
    PropulsionDrive,
)
from thrs.input_output.modules.lt1 import (
    Lt1SensorValues,
    Lt1SimulationInputs,
    Lt1SimulationOutputs,
)
from thrs.orchestration.runner import Runner
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import lt1_path

SEAWATER_TEMPERATURE = 20


@fixture
def simulation_inputs_inactive():
    return Lt1SimulationInputs(
        lt1_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_propdrive_aft1=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_aft2=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_fwd1=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_fwd2=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_shorepower=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        lt1_boilers_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(29)
        ),
    )


@fixture
def simulation_inputs_all_drives_active():
    return Lt1SimulationInputs(
        lt1_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_propdrive_aft1=PropulsionDrive(
            heat_flow=Stamped.stamp(2800), active=Stamped.stamp(True)
        ),
        lt1_propdrive_aft2=PropulsionDrive(
            heat_flow=Stamped.stamp(2800), active=Stamped.stamp(True)
        ),
        lt1_propdrive_fwd1=PropulsionDrive(
            heat_flow=Stamped.stamp(1250), active=Stamped.stamp(True)
        ),
        lt1_propdrive_fwd2=PropulsionDrive(
            heat_flow=Stamped.stamp(1250), active=Stamped.stamp(True)
        ),
        lt1_shorepower=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        lt1_boilers_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(29)
        ),
    )


@fixture
def simulation_inputs_shorepower():
    return Lt1SimulationInputs(
        lt1_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_propdrive_aft1=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_aft2=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_fwd1=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_fwd2=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_shorepower=Converter(
            heat_flow=Stamped.stamp(15000), active=Stamped.stamp(True)
        ),
        lt1_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        lt1_boilers_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(29)
        ),
    )


@fixture
def simulation(simulation_inputs_all_drives_active):
    with Fmu(lt1_path) as fmu:
        yield Simulation(
            Lt1SensorValues,
            Lt1SimulationOutputs,
            fmu,
            simulation_inputs_all_drives_active,
            datetime.now(),
            timedelta(seconds=1),
        )


@fixture()
def control(simulation) -> Lt1Control:
    return Lt1Control(Lt1Parameters(), simulation.time)


@fixture
def alarms() -> Lt1Alarms:
    return Lt1Alarms()


@fixture()
def runner(control: Lt1Control, simulation, alarms: Lt1Alarms) -> Runner:
    return Runner(simulation, control, alarms)
