from datetime import UTC, datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.dc import (
    DcControlValues,
    DcSensorValues,
    DcSimulationInputs,
    DcSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import dc_path


@fixture(
    params=list(simulator_input_field_setters(DcSimulationInputs, ignore=["dc_mode"]))
)
def incorrect_simulation_inputs(simulation_inputs, request):
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_simulation_step(control, simulation):
    result = simulation.tick(control.initial()[0])

    assert isinstance(result.simulation_outputs, DcSimulationOutputs)


def test_dc_simulation_inputs(incorrect_simulation_inputs):
    with Fmu(dc_path) as fmu:
        simulation = Simulation(
            DcSensorValues,
            DcSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(UTC),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for _i in range(300):
                simulation.tick(
                    DcControlValues.zero(),  # TODO: add actual control values
                )
