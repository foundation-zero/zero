from datetime import datetime, timedelta

from pytest import fixture

from thrs.control.modules.fahrenheit import FahrenheitControl, FahrenheitParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    Fahrenheit,
    TemperatureBoundary,
)
from thrs.input_output.modules.fahrenheit import (
    FahrenheitSensorValues,
    FahrenheitSimulationInputs,
    FahrenheitSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import fahrenheit_path


@fixture
def simulation_inputs():
    return FahrenheitSimulationInputs(
        fahrenheit_cold_supply=TemperatureBoundary(temperature=Stamped.stamp(20.0)),
        fahrenheit_seawater_supply=Boundary(
            temperature=Stamped.stamp(32.0), flow=Stamped.stamp(64.0)
        ),
        fahrenheit_available_cold_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(20.0)
        ),
        fahrenheit_available_hot_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(65.0)
        ),
        fahrenheit_available_seawater_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(30.0)
        ),
        fahrenheit_chiller=Fahrenheit(free_cooling=Stamped.stamp(False)),
        fahrenheit_ht_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(42.0)
        ),
        fahrenheit_boilers_supply=Boundary(
            temperature=Stamped.stamp(40.0), flow=Stamped.stamp(45.0)
        ),
    )


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        FahrenheitSensorValues,
        FahrenheitSimulationOutputs,
    )


@fixture
def control(simulation):
    return FahrenheitControl(FahrenheitParameters(), simulation.time)


@fixture
def simulation(io_mapping, simulation_inputs):
    with Fmu(fahrenheit_path) as fmu:
        yield Simulation(
            io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
        )
