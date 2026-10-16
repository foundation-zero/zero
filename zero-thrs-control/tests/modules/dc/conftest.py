from datetime import UTC, datetime, timedelta

from pytest import fixture

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.dc import DcAlarms, DcControl, DcParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    BrightloopString,
    HeatSource,
    Ugrid,
)
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
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
        dc_brightloop_fwd1=HeatSource(heat_flow=Stamped.stamp(0)),
        dc_brightloop_fwd2=HeatSource(heat_flow=Stamped.stamp(0)),
        dc_brightloop_aft1=HeatSource(heat_flow=Stamped.stamp(0)),
        dc_brightloop_aft2=HeatSource(heat_flow=Stamped.stamp(0)),
        dc_brightloop_aft3=HeatSource(heat_flow=Stamped.stamp(0)),
        dc_brightloop_aft4=HeatSource(heat_flow=Stamped.stamp(0)),
        dc_brightloop_fwd1_string1=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string2=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string3=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string4=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string1=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string2=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string3=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string4=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_ugrid1=Ugrid(
            heat_flow=Stamped.stamp(2000),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_ugrid2=Ugrid(
            heat_flow=Stamped.stamp(2000),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string1=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string2=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string3=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string4=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string1=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string2=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string3=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string1=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string2=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string3=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string1=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string2=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string3=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string4=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        dc_dhw_supply=Boundary(temperature=Stamped.stamp(35), flow=Stamped.stamp(20)),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def simulation_inputs_brightloops_aft_active():
    return DcSimulationInputs(
        dc_brightloop_fwd1=HeatSource(heat_flow=Stamped.stamp(0)),
        dc_brightloop_fwd2=HeatSource(heat_flow=Stamped.stamp(0)),
        dc_brightloop_aft1=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_aft2=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_aft3=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_aft4=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_fwd1_string1=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string2=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string3=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string4=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string1=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string2=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string3=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string4=BrightloopString(
            active=Stamped.stamp(False),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_ugrid1=Ugrid(
            heat_flow=Stamped.stamp(2000),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_ugrid2=Ugrid(
            heat_flow=Stamped.stamp(2000),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string4=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string4=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        dc_dhw_supply=Boundary(temperature=Stamped.stamp(35), flow=Stamped.stamp(20)),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def simulation_inputs():
    return DcSimulationInputs(
        dc_brightloop_fwd1=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_fwd2=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_aft1=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_aft2=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_aft3=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_aft4=HeatSource(heat_flow=Stamped.stamp(500)),
        dc_brightloop_fwd1_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd1_string4=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_fwd2_string4=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_ugrid1=Ugrid(
            heat_flow=Stamped.stamp(2000),
            active=Stamped.stamp(True),
            temp_power_stage=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_ugrid2=Ugrid(
            heat_flow=Stamped.stamp(2000),
            active=Stamped.stamp(True),
            temp_power_stage=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft1_string4=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft2_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft3_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string1=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string2=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string3=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_brightloop_aft4_string4=BrightloopString(
            active=Stamped.stamp(True),
            cell01_temperature1=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        dc_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        dc_dhw_supply=Boundary(temperature=Stamped.stamp(35), flow=Stamped.stamp(20)),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
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
            datetime.now(UTC),
            timedelta(seconds=1),
        )
