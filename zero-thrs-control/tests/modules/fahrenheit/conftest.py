from pytest import fixture

from thrs.control.modules.fahrenheit import FahrenheitControl, FahrenheitParameters
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    ExchangerBoundary,
    OverpressureTemperatureBoundary,
    TemperatureBoundary,
)
from thrs.input_output.modules.fahrenheit import (
    FahrenheitSensorValues,
    FahrenheitSimulationInputs,
    FahrenheitSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping
from thrs.simulation.models.fmu_paths import fahrenheit_path
from datetime import datetime, timedelta


@fixture
def simulation_inputs():
    return FahrenheitSimulationInputs(
        fahrenheit_hot_supply=ExchangerBoundary(
            temperature=Stamped.stamp(60.0),
            flow=Stamped.stamp(42.0),
            overpressure=Stamped.stamp(2.0),
        ),
        fahrenheit_waste_supply=ExchangerBoundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(45.0),
            overpressure=Stamped.stamp(2.0),
        ),
        fahrenheit_cold_supply=OverpressureTemperatureBoundary(
            temperature=Stamped.stamp(15.0), overpressure=Stamped.stamp(2.0)
        ),
        fahrenheit_seawater_supply=Boundary(
            temperature=Stamped.stamp(32.0), flow=Stamped.stamp(64.0)
        ),
        fahrenheit_available_hot_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(70.0)
        ),
        fahrenheit_available_cold_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(10.0)
        ),
        fahrenheit_available_seawater_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(32.0)
        ),
    )


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        FahrenheitSensorValues,
        FahrenheitSimulationOutputs,
    )


@fixture
def control(executor):
    return FahrenheitControl(FahrenheitParameters(), executor.time)


@fixture
def executor(io_mapping, simulation_inputs):
    with Fmu(fahrenheit_path) as fmu:
        yield SimulationExecutor(
            io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
        )
