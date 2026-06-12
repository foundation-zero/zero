from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from thrs.control.modules.consumers import ConsumersParameters
from thrs.control.modules.pcm import PcmParameters
from thrs.control.modules.pvt import PvtParameters
from thrs.control.modules.thrusters import ThrustersParameters
from thrs.input_output.base import CombinedValues
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
)
from thrs.orchestration.runner import ModuleSimulatorModel, Runner
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import high_temperature_path


@fixture(
    params=list(
        simulator_input_field_setters(
            HighTemperatureSimulationInputs,
            ignore=[
                (
                    "consumers_fahrenheit_supply",
                    "flow",
                ),  # Flows appear to just work, instead of break
                ("pvt_pump_failure_switch_main_aft", "position_rel"),
                ("pvt_pump_failure_switch_main_fwd", "position_rel"),
                (
                    "pvt_pump_failure_switch_owners",
                    "position_rel",
                ),  # TODO: figure out why this takes such a long time. Could be related to flow control.
            ],
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


async def test_high_temperature_simulation_inputs(
    incorrect_simulation_inputs, control, module
):
    with Fmu(high_temperature_path) as fmu:
        simulation = Simulation(
            module.sensor_values_clss,
            module.simulation_outputs_cls,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for i in range(300):
                await simulation.tick(
                    control.initial(datetime.now()).values,
                )


async def test_module_simulator_model(module):
    params = CombinedValues(
        values={
            "thrusters": ThrustersParameters(),
            "pvt": PvtParameters(),
            "pcm": PcmParameters(),
            "consumers": ConsumersParameters(),
        }
    )
    inputs = HighTemperatureSimulationInputs.zero()
    model = ModuleSimulatorModel(
        fmu_path=high_temperature_path,
        module=module,
        simulation_inputs=inputs,
    )
    with model.simulation() as simulation:
        simulation.transceive = simulation.tick  # type: ignore # TODO: Make this make sense
        runner = Runner.from_module(module, params, simulation)  # type: ignore # TODO: Make this make sense

        await runner.run(100)
