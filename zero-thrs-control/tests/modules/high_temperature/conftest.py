from datetime import datetime, timedelta
from pytest import fixture

from thrs.control.modules.high_temperature import (
    HighTemperatureControl,
    HighTemperatureParameters,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    FmuBoundary,
    HeatSource,
    Pcs,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSensorValues,
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import IoMapping
from thrs.simulation.models.fmu_paths import high_temperature_path


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
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(8000)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
        consumers_fahrenheit_supply=FmuBoundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(42),
            overpressure=Stamped.stamp(0.2),
        ),
        consumers_boosting_supply=FmuBoundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(29),
            overpressure=Stamped.stamp(0.2),
        ),
    )


@fixture
def control(executor):
    return HighTemperatureControl(HighTemperatureParameters(), executor.time)


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
