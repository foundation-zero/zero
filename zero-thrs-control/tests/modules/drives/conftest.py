from datetime import UTC, datetime, timedelta

from pytest import fixture

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.drives import DrivesAlarms, DrivesControl, DrivesParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    PropulsionDrive,
    ShorePowerConverter,
)
from thrs.input_output.definitions.system import AmcsControlMode, ControlMode
from thrs.input_output.modules.drives import (
    DrivesSensorValues,
    DrivesSimulationInputs,
    DrivesSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import drives_path

SEAWATER_TEMPERATURE = 20


@fixture
def simulation_inputs_inactive():
    return DrivesSimulationInputs(
        drives_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_propdrive_aft1=PropulsionDrive(
            heat_flow=Stamped.stamp(0),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_aft2=PropulsionDrive(
            heat_flow=Stamped.stamp(0),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_fwd1=PropulsionDrive(
            heat_flow=Stamped.stamp(0),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_fwd2=PropulsionDrive(
            heat_flow=Stamped.stamp(0),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_shorepower=HeatSource(
            heat_flow=Stamped.stamp(0),
        ),
        drives_shorepower1a=ShorePowerConverter(
            active=Stamped.stamp(False),
            esi_igbt_max_temperature=Stamped.stamp(23),
            esi_igbt_min_temperature=Stamped.stamp(23),
            esi_transformer_temperature=Stamped.stamp(23),
            power=Stamped.stamp(0),
        ),
        drives_shorepower1b=ShorePowerConverter(
            active=Stamped.stamp(False),
            esi_igbt_max_temperature=Stamped.stamp(23),
            esi_igbt_min_temperature=Stamped.stamp(23),
            esi_transformer_temperature=Stamped.stamp(23),
            power=Stamped.stamp(0),
        ),
        drives_shorepower2a=ShorePowerConverter(
            active=Stamped.stamp(False),
            esi_igbt_max_temperature=Stamped.stamp(23),
            esi_igbt_min_temperature=Stamped.stamp(23),
            esi_transformer_temperature=Stamped.stamp(23),
            power=Stamped.stamp(0),
        ),
        drives_shorepower2b=ShorePowerConverter(
            active=Stamped.stamp(False),
            esi_igbt_max_temperature=Stamped.stamp(23),
            esi_igbt_min_temperature=Stamped.stamp(23),
            esi_transformer_temperature=Stamped.stamp(23),
            power=Stamped.stamp(0),
        ),
        drives_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        drives_dhw_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(29)
        ),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def simulation_inputs_all_drives_active():
    return DrivesSimulationInputs(
        drives_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_propdrive_aft1=PropulsionDrive(
            heat_flow=Stamped.stamp(2800),
            active=Stamped.stamp(True),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_aft2=PropulsionDrive(
            heat_flow=Stamped.stamp(2800),
            active=Stamped.stamp(True),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_fwd1=PropulsionDrive(
            heat_flow=Stamped.stamp(1250),
            active=Stamped.stamp(True),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_fwd2=PropulsionDrive(
            heat_flow=Stamped.stamp(1250),
            active=Stamped.stamp(True),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_shorepower=HeatSource(
            heat_flow=Stamped.stamp(0),
        ),
        drives_shorepower1a=ShorePowerConverter(
            active=Stamped.stamp(False),
            esi_igbt_max_temperature=Stamped.stamp(23),
            esi_igbt_min_temperature=Stamped.stamp(23),
            esi_transformer_temperature=Stamped.stamp(23),
            power=Stamped.stamp(0),
        ),
        drives_shorepower1b=ShorePowerConverter(
            active=Stamped.stamp(False),
            esi_igbt_max_temperature=Stamped.stamp(23),
            esi_igbt_min_temperature=Stamped.stamp(23),
            esi_transformer_temperature=Stamped.stamp(23),
            power=Stamped.stamp(0),
        ),
        drives_shorepower2a=ShorePowerConverter(
            active=Stamped.stamp(False),
            esi_igbt_max_temperature=Stamped.stamp(23),
            esi_igbt_min_temperature=Stamped.stamp(23),
            esi_transformer_temperature=Stamped.stamp(23),
            power=Stamped.stamp(0),
        ),
        drives_shorepower2b=ShorePowerConverter(
            active=Stamped.stamp(False),
            esi_igbt_max_temperature=Stamped.stamp(23),
            esi_igbt_min_temperature=Stamped.stamp(23),
            esi_transformer_temperature=Stamped.stamp(23),
            power=Stamped.stamp(0),
        ),
        drives_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        drives_dhw_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(29)
        ),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def simulation_inputs_shorepower():
    return DrivesSimulationInputs(
        drives_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_propdrive_aft1=PropulsionDrive(
            heat_flow=Stamped.stamp(0),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_aft2=PropulsionDrive(
            heat_flow=Stamped.stamp(0),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_fwd1=PropulsionDrive(
            heat_flow=Stamped.stamp(0),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_propdrive_fwd2=PropulsionDrive(
            heat_flow=Stamped.stamp(0),
            active=Stamped.stamp(False),
            temp_power_stage=Stamped.stamp(0),
            power=Stamped.stamp(0),
        ),
        drives_shorepower=HeatSource(
            heat_flow=Stamped.stamp(15000),
        ),
        drives_shorepower1a=ShorePowerConverter(
            active=Stamped.stamp(True),
            esi_igbt_max_temperature=Stamped.stamp(100),
            esi_igbt_min_temperature=Stamped.stamp(100),
            esi_transformer_temperature=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        drives_shorepower1b=ShorePowerConverter(
            active=Stamped.stamp(True),
            esi_igbt_max_temperature=Stamped.stamp(100),
            esi_igbt_min_temperature=Stamped.stamp(100),
            esi_transformer_temperature=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        drives_shorepower2a=ShorePowerConverter(
            active=Stamped.stamp(True),
            esi_igbt_max_temperature=Stamped.stamp(100),
            esi_igbt_min_temperature=Stamped.stamp(100),
            esi_transformer_temperature=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        drives_shorepower2b=ShorePowerConverter(
            active=Stamped.stamp(True),
            esi_igbt_max_temperature=Stamped.stamp(100),
            esi_igbt_min_temperature=Stamped.stamp(100),
            esi_transformer_temperature=Stamped.stamp(100),
            power=Stamped.stamp(1000),
        ),
        drives_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        drives_dhw_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(29)
        ),
        mode=AmcsControlMode(mode=Stamped.stamp(ControlMode.EXTERNAL)),
    )


@fixture
def simulation(simulation_inputs_all_drives_active):
    with Fmu(drives_path) as fmu:
        yield Simulation(
            DrivesSensorValues,
            DrivesSimulationOutputs,
            fmu,
            simulation_inputs_all_drives_active,
            datetime.now(UTC),
            timedelta(seconds=1),
        )


@fixture()
def control(simulation) -> DrivesControl:
    return DrivesControl(
        DrivesParameters(), simulation.time, MachineStateLoggingServiceNoop()
    )


@fixture
def alarms() -> DrivesAlarms:
    return DrivesAlarms()


@fixture()
def runner(
    control: DrivesControl,
    simulation,
    simulation_inputs_all_drives_active,
    alarms: DrivesAlarms,
) -> SimulationTestRunner:
    return SimulationTestRunner(
        simulation, simulation_inputs_all_drives_active, control, alarms
    )
