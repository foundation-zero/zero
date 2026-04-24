from datetime import datetime, timedelta
from pytest import fixture
from thrs.classes.machine_state_logger import MachineStateLoggingService
from thrs.control.modules.thrusters import (
    ThrustersAlarms,
    ThrustersControl,
    ThrustersParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import thrusters_path

type ThrustersSimulationExecutor = SimulationExecutor[
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
]


@fixture
def simulation_inputs():
    return ThrustersSimulationInputs(
        thrusters_aft=Thruster(
            heat_flow=Stamped.stamp(9000), active=Stamped.stamp(True)
        ),
        thrusters_fwd=Thruster(
            heat_flow=Stamped.stamp(4300), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        thrusters_module_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
    )


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
    )


@fixture
def control(executor):
    return ThrustersControl(
        ThrustersParameters(), executor.time, MachineStateLoggingService()
    )


@fixture
def executor(fmu, io_mapping, simulation_inputs) -> ThrustersSimulationExecutor:
    return SimulationExecutor(
        io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
    )


@fixture
def fmu():
    with Fmu(thrusters_path) as fmu:
        yield fmu


@fixture
def alarms() -> ThrustersAlarms:
    return ThrustersAlarms()
