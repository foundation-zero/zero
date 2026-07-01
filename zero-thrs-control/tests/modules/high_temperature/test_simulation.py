from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.input_output.modules.consumers import ConsumersSensorValues
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import PcmSensorValues
from thrs.input_output.modules.pvt import PvtSensorValues
from thrs.input_output.modules.thrusters import ThrustersSensorValues
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import high_temperature_path


@fixture(
    params=list(
        simulator_input_field_setters(HighTemperatureSimulationInputs, ignore=[])
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


def test_high_temperature_simulation_inputs(
    control, simulation, incorrect_simulation_inputs
):
    with Fmu(high_temperature_path) as fmu:
        simulation = Simulation(
            {
                "thrusters": ThrustersSensorValues,
                "pvt": PvtSensorValues,
                "pcm": PcmSensorValues,
                "consumers": ConsumersSensorValues,
            },
            HighTemperatureSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for i in range(300):
                simulation.tick(
                    control.initial(datetime.now()),
                )
