from datetime import UTC, datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.input_output.base import CombinedValues
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
        simulator_input_field_setters(
            HighTemperatureSimulationInputs,
            ignore=[
                ("thrusters_seawater_supply", "flow"),
                ("pvt_seawater_supply", "flow"),
                ("pcm_freshwater_supply", "flow"),
                "mode",
            ],  # Do not throw an exception
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    request.param(simulation_inputs, -9e7)
    return simulation_inputs


def test_high_temperature_simulation_inputs(
    modules, simulation, incorrect_simulation_inputs
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
            datetime.now(UTC),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for _i in range(300):
                simulation.tick(
                    CombinedValues(
                        {
                            module_name: module.control(
                                module.parameters_cls(),
                                simulation.time,
                                MachineStateLoggingServiceNoop(),
                            ).initial()[0]
                            for module_name, module in modules.items()
                        }
                    )
                )


def test_high_temperature_simulation_ticks(modules, simulation):
    result = simulation.tick(
        CombinedValues(
            {
                module_name: module.control(
                    module.parameters_cls(),
                    simulation.time,
                    MachineStateLoggingServiceNoop(),
                ).initial()[0]
                for module_name, module in modules.items()
            }
        )
    )

    pcm_sensor_values = result.sensor_values.values["pcm"]
    assert pcm_sensor_values.freshwater_temperature_pcm_supply.temperature.value == (
        result.simulation_inputs.pcm_freshwater_supply.temperature.value
    )
