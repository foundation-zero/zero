from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.drives import (
    DrivesSensorValues,
    DrivesSimulationInputs,
    DrivesSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import drives_path


@fixture(params=list(simulator_input_field_setters(DrivesSimulationInputs)))
def incorrect_simulation_inputs(simulation_inputs_inactive, request):
    inputs = simulation_inputs_inactive.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


def test_simulation_step(control, simulation):
    result = simulation.tick(control.initial()[0])

    assert isinstance(result.simulation_outputs, DrivesSimulationOutputs)


def test_drives_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(drives_path) as fmu:
        simulation = Simulation(
            DrivesSensorValues,
            DrivesSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for _i in range(300):
                simulation.tick(control.initial(datetime.now()))
