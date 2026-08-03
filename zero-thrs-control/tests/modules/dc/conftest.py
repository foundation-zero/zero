from datetime import datetime, timedelta

from pytest import fixture

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.dc import DcAlarms, DcControl, DcParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary, Converter
from thrs.input_output.modules.dc import (
    DcSensorValues,
    DcSimulationInputs,
    DcSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import dc_path

SEAWATER_TEMPERATURE = 20


@fixture
def simulation_inputs_inactive():
    return DcSimulationInputs(
        dc_brightloop_fwd1=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_fwd2=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_ugrid1=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        dc_ugrid2=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        dc_brightloop_aft1=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_aft2=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_aft3=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_aft4=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        dc_dhw_supply=Boundary(temperature=Stamped.stamp(35), flow=Stamped.stamp(20)),
    )


@fixture
def simulation_inputs_brightloops_aft_active():
    return DcSimulationInputs(
        dc_brightloop_fwd1=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_fwd2=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_ugrid1=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        dc_ugrid2=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        dc_brightloop_aft1=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft2=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft3=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft4=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        dc_dhw_supply=Boundary(temperature=Stamped.stamp(35), flow=Stamped.stamp(20)),
    )


@fixture
def simulation_inputs():
    return DcSimulationInputs(
        dc_brightloop_fwd1=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_fwd2=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_ugrid1=Converter(heat_flow=Stamped.stamp(2000), active=Stamped.stamp(True)),
        dc_ugrid2=Converter(heat_flow=Stamped.stamp(2000), active=Stamped.stamp(True)),
        dc_brightloop_aft1=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft2=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft3=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft4=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        dc_dhw_supply=Boundary(temperature=Stamped.stamp(35), flow=Stamped.stamp(20)),
    )


@fixture()
def control(simulation) -> DcControl:
    return DcControl(DcParameters(), simulation.time, MachineStateLoggingServiceNoop())


@fixture
def alarms() -> DcAlarms:
    return DcAlarms()


@fixture()
def runner(
    control: DcControl, simulation, simulation_inputs, alarms: DcAlarms
) -> SimulationTestRunner:
    return SimulationTestRunner(simulation, simulation_inputs, control, alarms)


@fixture
def simulation(simulation_inputs):
    with Fmu(dc_path) as fmu:
        yield Simulation(
            DcSensorValues,
            DcSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )
