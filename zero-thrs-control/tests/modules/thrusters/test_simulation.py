from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.collector import PolarsCollector
from tests.helpers.simulation_inputs import simulator_input_field_setters
from tests.helpers.simulation_runner import SimulationTestRunner
from tests.modules.thrusters.conftest import ThrustersSimulation
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.thrusters import (
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import thrusters_path


def test_computed_collection(
    simulation: ThrustersSimulation, simulation_inputs, control, alarms
):
    collector = PolarsCollector()
    runner = SimulationTestRunner(simulation, simulation_inputs, control, alarms)
    runner.run(20, collector)
    frame = collector.result()
    assert frame is not None
    assert "thrusters_temperature_recovery__temperature__C" in frame.columns


def test_simulation(simulation, simulation_inputs, control, alarms):
    runner = SimulationTestRunner(simulation, simulation_inputs, control, alarms)

    collector = PolarsCollector()

    runner.run(20, collector)

    result = collector.result()
    assert result is not None
    assert result["time"].len() == 20


@fixture(params=list(simulator_input_field_setters(ThrustersSimulationInputs)))
def incorrect_simulation_inputs(
    simulation_inputs: ThrustersSimulationInputs, request: pytest.FixtureRequest
) -> ThrustersSimulationInputs:
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(thrusters_path) as fmu:
        simulation = Simulation(
            ThrustersSensorValues,
            ThrustersSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=5),
        )

        control_values, _ = control.initial()

        control_values.thrusters_pump1.dutypoint.value = 1
        control_values.thrusters_mix_recovery.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.thrusters_flowcontrol_aft.setpoint.value = Valve.OPEN
        control_values.thrusters_flowcontrol_fwd.setpoint.value = Valve.OPEN
        control_values.thrusters_pump1.on.value = True

        with pytest.raises(Exception):
            for _i in range(100):
                simulation.tick(
                    control._current_values,
                )
