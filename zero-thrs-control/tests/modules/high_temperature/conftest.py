from datetime import datetime, timedelta
from pytest import fixture

from control.modules.high_temperature import HighTemperatureControl, HighTemperatureParameters
from input_output.base import Stamped
from input_output.definitions.control import Valve
from input_output.definitions.simulation import Boundary, HeatSource, Pcs, Thruster, ValvePosition
from input_output.modules.high_temperature import HighTemperatureSensorValues, HighTemperatureSimulationInputs, HighTemperatureSimulationOutputs
from orchestration.executor import SimulationExecutor
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping
from simulation.models.fmu_paths import high_temperature_path




@fixture
def simulation_inputs():
    return HighTemperatureSimulationInputs(
         thrusters_aft=Thruster(
            heat_flow=Stamped.stamp(9000), active=Stamped.stamp(True)
        ),
        thrusters_fwd=Thruster(
            heat_flow=Stamped.stamp(4300), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        thrusters_pcs=Pcs(mode=Stamped.stamp("propulsion")),
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
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
        consumers_fahrenheit_supply=Boundary(
            temperature=Stamped.stamp(60), flow=Stamped.stamp(42)
        ),
        consumers_boosting_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(29)
        ),
    )

@fixture
def control():
    return HighTemperatureControl(HighTemperatureParameters())

@fixture
def io_mapping():
    with Fmu(high_temperature_path) as fmu:
        yield IoMapping(
            fmu,
            HighTemperatureSensorValues,
            HighTemperatureSimulationOutputs,
        )

@fixture
def executor(io_mapping, simulation_inputs):
    return SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=1)
    )
