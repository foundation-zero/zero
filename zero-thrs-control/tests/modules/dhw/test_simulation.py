from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.collector import PolarsCollector
from tests.helpers.simulation_inputs import simulator_input_field_setters
from tests.helpers.simulation_runner import SimulationTestRunner
from thrs.input_output.modules.dhw import (
    DhwControlValues,
    DhwSensorValues,
    DhwSimulationInputs,
    DhwSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import dc_path


def test_simulation(simulation, control, alarms):
    runner = SimulationTestRunner(simulation, control, alarms)

    collector = PolarsCollector()

    runner.run(20, collector)

    result = collector.result()
    assert result is not None
    assert result["time"].len() == 20


@fixture(params=list(simulator_input_field_setters(DhwSimulationInputs)))
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


def test_simulation_step(control, simulation):
    result = simulation.tick(control.initial()[0])

    assert isinstance(result.simulation_outputs, DhwSimulationOutputs)


def test_dhw_simulation_inputs(incorrect_simulation_inputs):
    with Fmu(dc_path) as fmu:
        simulation = Simulation(
            DhwSensorValues,
            DhwSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for _i in range(300):
                simulation.tick(
                    DhwControlValues.zero(),
                )
