from datetime import datetime, timedelta
from pytest import fixture
from thrs.control.modules.pvt import PvtControl, PvtParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    TemperatureBoundary,
    ValvePosition,
)
from thrs.input_output.modules.pvt import (
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import IoMapping
from thrs.simulation.models.fmu_paths import pvt_path


@fixture
def simulation_inputs():
    return PvtSimulationInputs(
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(8000)),
        pvt_module_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
    )


@fixture
def pump_failure_simulation_inputs(simulation_inputs):
    simulation_inputs.pvt_pump_failure_switch_main_fwd = ValvePosition(
        position_rel=Stamped.stamp(Valve.OPEN)
    )
    simulation_inputs.pvt_pump_failure_switch_main_aft = ValvePosition(
        position_rel=Stamped.stamp(Valve.OPEN)
    )
    simulation_inputs.pvt_pump_failure_switch_owners = ValvePosition(
        position_rel=Stamped.stamp(Valve.OPEN)
    )
    return simulation_inputs


@fixture
def io_mapping():
    with Fmu(pvt_path) as fmu:
        yield IoMapping(
            fmu,
            PvtSensorValues,
            PvtSimulationOutputs,
        )


@fixture
def control(executor):
    return PvtControl(PvtParameters(), executor.time)


@fixture
def executor(io_mapping, simulation_inputs):
    return SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=1)
    )


@fixture
def pump_failure_executor(io_mapping, pump_failure_simulation_inputs):
    return SimulationExecutor(
        io_mapping, pump_failure_simulation_inputs, datetime.now(), timedelta(seconds=1)
    )
