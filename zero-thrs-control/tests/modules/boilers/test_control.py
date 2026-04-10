from pytest import approx

from thrs.input_output.base import Stamped
from thrs.input_output.modules.boilers import BoilersSimulationInputs
from thrs.orchestration.cycler import Cycler
from thrs.orchestration.executor import SimulationExecutionResult


async def test_filling(cycler: Cycler, simulation_inputs: BoilersSimulationInputs):
    result = await cycler.run(60)

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_lt1.flow.value > 0.1
    assert result.sensor_values.boilers_flow_lt2.flow.value > 0.1

    simulation_inputs_no_lt1 = simulation_inputs.model_copy(
        update={
            "boilers_lt1_supply": simulation_inputs.boilers_lt1_supply.copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    cycler.update_simulation_inputs(simulation_inputs_no_lt1)

    result = await cycler.run(60)

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_lt1.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.boilers_flow_lt2.flow.value > 0.1

    cycler._control.update_parameters(
        cycler._control.parameters.copy(update={"maximum_tank_level": 10})
    )

    result = await cycler.run(180)
    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_lt1.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.boilers_flow_lt2.flow.value == approx(0.0, abs=0.01)
