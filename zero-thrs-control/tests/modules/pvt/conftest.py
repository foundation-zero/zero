from datetime import timedelta
from pathlib import Path
from pytest import fixture
from control.modules.pvt import PvtControl, PvtParameters
from input_output.base import Stamped
from input_output.definitions.control import Valve
from input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    TemperatureBoundary,
    ValvePosition,
)
from input_output.modules.pvt import (
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping


@fixture
def fmu_path():
    return str(
        Path(__file__).resolve().parent.parent.parent.parent
        / "src/simulation/models/pvt/pvt_moduleV2.fmu"
    )


@fixture
def simulation_inputs():
    return PvtSimulationInputs(
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(8000)),
        pvt_pump_failure_switch_main_fwd=ValvePosition(
            position_rel=Stamped.stamp(Valve.CLOSED)
        ),
        pvt_pump_failure_switch_main_aft=ValvePosition(
            position_rel=Stamped.stamp(Valve.CLOSED)
        ),
        pvt_pump_failure_switch_owners=ValvePosition(
            position_rel=Stamped.stamp(Valve.CLOSED)
        ),
        pvt_module_supply=TemperatureBoundary(temperature=Stamped.stamp(65)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
    )


@fixture
def io_mapping(fmu_path) -> IoMapping:
    return IoMapping(
        Fmu(
            fmu_path,
            timedelta(seconds=0.001),
        ),
        PvtSensorValues,
        PvtSimulationOutputs,
    )


@fixture
def control() -> PvtControl:
    return PvtControl(PvtParameters())
