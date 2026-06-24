from datetime import datetime, timedelta

from pytest import fixture

from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.control.modules.dhw import (
    DhwAlarms,
    DhwControl,
    DhwControlMode,
    DhwParameters,
    Tank,
    TanksController,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import (
    Boundary,
    FlowBoundary,
    HvacExchanger,
    OverpressureTemperatureBoundary,
    TemperatureBoundary,
)
from thrs.input_output.modules.dhw import (
    DhwControlValues,
    DhwSensorValues,
    DhwSimulationInputs,
    DhwSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import dhw_path


@fixture
def simulation_inputs():
    return DhwSimulationInputs(
        dhw_drives_supply=Boundary(
            temperature=Stamped.stamp(50),
            flow=Stamped.stamp(35),
        ),
        dhw_dc_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
        ),
        dhw_adsorption_supply=Boundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(45),
        ),
        dhw_ht_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
        ),
        dhw_freshwater_supply=OverpressureTemperatureBoundary(
            temperature=Stamped.stamp(20),
            overpressure=Stamped.stamp(0.1),
        ),
        dhw_hvac_exchanger=HvacExchanger(
            heat_flow=Stamped.stamp(300), maximum_temperature=Stamped.stamp(35)
        ),
        dhw_seawater_supply=TemperatureBoundary(temperature=Stamped.stamp(32)),
        dhw_hotwater_demand=FlowBoundary(flow=Stamped.stamp(20)),
    )


@fixture
def simulation(simulation_inputs):
    with Fmu(dhw_path) as fmu:
        yield Simulation[
            DhwSensorValues, DhwControlValues, DhwSimulationInputs, DhwSimulationOutputs
        ](
            DhwSensorValues,
            DhwSimulationOutputs,
            fmu,
            simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )


@fixture
def control(simulation) -> DhwControl:
    return DhwControl(DhwParameters(), simulation.time)


@fixture
def alarms() -> DhwAlarms:
    return DhwAlarms()


@fixture
def parameters() -> DhwParameters:
    return DhwParameters()


@fixture()
def runner(
    control: DhwControl,
    simulation: Simulation[
        DhwSensorValues, DhwControlValues, DhwSimulationInputs, DhwSimulationOutputs
    ],
    alarms: DhwAlarms,
) -> SimulationTestRunner[
    DhwSensorValues,
    DhwControlValues,
    DhwSimulationInputs,
    DhwSimulationOutputs,
    DhwParameters,
    DhwControlMode,
]:
    return SimulationTestRunner(simulation, control, alarms)


@fixture
def sensor_values() -> DhwSensorValues:
    return DhwSensorValues.zero()


@fixture
def tanks_controller(parameters) -> TanksController:
    control_values = DhwControlValues.zero()
    return TanksController(
        tank1=Tank(
            inlet=control_values.dhw_switch_tank1_inlet,
            outlet=control_values.dhw_switch_tank1_outlet,
            boosting_supply_valve=control_values.dhw_switch_tank1_boosting_supply,
            boosting_return_valve=control_values.dhw_switch_tank1_boosting_return,
            disabled=parameters.tank1_disabled,
        ),
        tank2=Tank(
            inlet=control_values.dhw_switch_tank2_inlet,
            outlet=control_values.dhw_switch_tank2_outlet,
            boosting_supply_valve=control_values.dhw_switch_tank2_boosting_supply,
            boosting_return_valve=control_values.dhw_switch_tank2_boosting_return,
            disabled=parameters.tank2_disabled,
        ),
        tank3=Tank(
            inlet=control_values.dhw_switch_tank3_inlet,
            outlet=control_values.dhw_switch_tank3_outlet,
            boosting_supply_valve=control_values.dhw_switch_tank3_boosting_supply,
            boosting_return_valve=control_values.dhw_switch_tank3_boosting_return,
            disabled=parameters.tank3_disabled,
        ),
        time_fn=lambda: datetime.now(),
    )
