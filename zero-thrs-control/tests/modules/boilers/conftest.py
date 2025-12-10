from datetime import datetime, timedelta
from pytest import fixture

from thrs.control.modules.boilers import (
    BoilersControl,
    BoilersParameters,
    Tank,
    TanksController,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    FmuBoundary,
    PressureBoundary,
    TemperatureBoundary,
)
from thrs.input_output.modules.boilers import (
    BoilersControlValues,
    BoilersSensorValues,
    BoilersSimulationInputs,
    BoilersSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping

from thrs.simulation.models.fmu_paths import boilers_path


@fixture
def simulation_inputs():
    return BoilersSimulationInputs(
        boilers_propdrive_shore_supply=FmuBoundary(
            temperature=Stamped.stamp(50),
            flow=Stamped.stamp(35),
            overpressure=Stamped.stamp(1.5),
        ),
        boilers_fahrenheit_supply=FmuBoundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(45),
            overpressure=Stamped.stamp(1.5),
        ),
        boilers_converters_supply=FmuBoundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
            overpressure=Stamped.stamp(1.5),
        ),
        boilers_high_temperature_supply=FmuBoundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
            overpressure=Stamped.stamp(1.5),
        ),
        boilers_freshwater_supply=TemperatureBoundary(temperature=Stamped.stamp(20)),
        boilers_freshwater_pressure=PressureBoundary(pressure=Stamped.stamp(3)),
    )


@fixture
def io_mapping():
    return ThrsModelIoMapping(
        BoilersSensorValues,
        BoilersSimulationOutputs,
    )


@fixture
def executor(io_mapping, simulation_inputs):
    with Fmu(boilers_path) as fmu:
        yield SimulationExecutor(
            io_mapping, fmu, simulation_inputs, datetime.now(), timedelta(seconds=1)
        )


@fixture
def control(executor) -> BoilersControl:
    return BoilersControl(BoilersParameters(), executor.time)


@fixture
def parameters() -> BoilersParameters:
    return BoilersParameters()


@fixture
def sensor_values() -> BoilersSensorValues:
    return BoilersSensorValues.zero()


@fixture
def tanks_controller(test_time, parameters) -> TanksController:
    control_values = BoilersControlValues.zero()
    return TanksController(
        tank1=Tank(
            fill_valve=control_values.boilers_switch_tank1_fill,
            empty_valve=control_values.boilers_switch_tank1_empty,
            boosting_supply_valve=control_values.boilers_switch_tank1_boosting_supply,
            boosting_return_valve=control_values.boilers_switch_tank1_boosting_return,
            disabled=parameters.tank1_disabled,
        ),
        tank2=Tank(
            fill_valve=control_values.boilers_switch_tank2_fill,
            empty_valve=control_values.boilers_switch_tank2_empty,
            boosting_supply_valve=control_values.boilers_switch_tank2_boosting_supply,
            boosting_return_valve=control_values.boilers_switch_tank2_boosting_return,
            disabled=parameters.tank2_disabled,
        ),
        tank3=Tank(
            fill_valve=control_values.boilers_switch_tank3_fill,
            empty_valve=control_values.boilers_switch_tank3_empty,
            boosting_supply_valve=control_values.boilers_switch_tank3_boosting_supply,
            boosting_return_valve=control_values.boilers_switch_tank3_boosting_return,
            disabled=parameters.tank3_disabled,
        ),
        time_fn=test_time.time,
    )
