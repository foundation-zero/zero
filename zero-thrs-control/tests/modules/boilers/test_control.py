from pytest import approx

from thrs.control.modules.boilers import BoilersControl, TanksController
from thrs.input_output.base import Stamped
from thrs.input_output.modules.boilers import BoilersSimulationInputs
from thrs.orchestration.executor import SimulationExecutionResult
from thrs.orchestration.runner import Runner


async def test_filling(runner: Runner, simulation_inputs: BoilersSimulationInputs):
    simulation_inputs_no_consumption = simulation_inputs.model_copy(
        update={
            "boilers_freshwater_return_set": simulation_inputs.boilers_hotwater_demand.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    runner._executor.update_simulation_inputs(simulation_inputs_no_consumption)  # type: ignore

    await runner.run(60)
    result = runner.last_tick_result

    assert isinstance(runner._control, BoilersControl)
    assert runner._control._lt1_flow_controller.enabled()
    assert runner._control._lt2_flow_controller.enabled()

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_lt1.flow.value > 0.1
    assert result.sensor_values.boilers_flow_lt2.flow.value > 0.1

    simulation_inputs_no_lt1 = simulation_inputs.model_copy(
        update={
            "boilers_lt1_supply": simulation_inputs.boilers_lt1_supply.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    runner._executor.update_simulation_inputs(simulation_inputs_no_lt1)  # type: ignore

    await runner.run(180)
    result = runner.last_tick_result

    assert isinstance(runner._control, BoilersControl)
    assert not runner._control._lt1_flow_controller.enabled()
    assert runner._control._lt2_flow_controller.enabled()

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_lt1.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.boilers_flow_lt2.flow.value > 0.1

    # wait for tanks to fill
    await runner.run(1000)
    result = runner.last_tick_result

    assert isinstance(result, SimulationExecutionResult)
    assert isinstance(runner._control, BoilersControl) and isinstance(
        runner._control._tanks_controller, TanksController
    )
    assert not runner._control._tanks_controller.filling
    assert not runner._control._lt1_flow_controller.enabled()
    assert not runner._control._lt2_flow_controller.enabled()

    assert result.sensor_values.boilers_flow_lt1.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.boilers_flow_lt2.flow.value == approx(0.0, abs=0.01)
    assert (
        result.sensor_values.boilers_level_tank1.level.value
        > runner._control.parameters.minimum_tank_level
    )
    assert (
        result.sensor_values.boilers_level_tank2.level.value
        > runner._control.parameters.minimum_tank_level
    )
    assert (
        result.sensor_values.boilers_level_tank3.level.value
        > runner._control.parameters.minimum_tank_level
    )


async def test_boosting_transitions(
    runner: Runner, simulation_inputs: BoilersSimulationInputs
):
    # all tanks full and ht available
    runner._control.update_parameters(
        runner._control.parameters.copy(update={"maximum_tank_level": 10})
    )

    await runner.run(120)
    result = runner.last_tick_result

    assert isinstance(runner._control, BoilersControl) and isinstance(
        runner._control._tanks_controller, TanksController
    )
    assert runner._control._tanks_controller.boosting
    assert runner._control.mode.is_boosting_high_temperature
    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_boosting.flow.value > 0.1
    assert (
        result.sensor_values.boilers_temperature_boosting_return.temperature.value
        < result.sensor_values.boilers_temperature_boosting_supply.temperature.value
    )

    # filling and no ht available (switch to heat pump)
    simulation_inputs_no_ht = simulation_inputs.model_copy(
        update={
            "boilers_ht_supply": simulation_inputs.boilers_ht_supply.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    runner._executor.update_simulation_inputs(simulation_inputs_no_ht)  # type: ignore
    await runner.run(120)
    result = runner.last_tick_result

    assert runner._control._tanks_controller.boosting
    assert runner._control.mode.is_boosting_heatpump
    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_boosting.flow.value == approx(25, abs=0.2)
    assert (
        result.sensor_values.boilers_temperature_boosting_return.temperature.value
        < result.sensor_values.boilers_temperature_boosting_supply.temperature.value
    )

    # all tanks at temperature
    runner._control.update_parameters(
        runner._control.parameters.copy(update={"maximum_tank_temperature": 10})
    )
    await runner.run(120)
    result = runner.last_tick_result

    assert not runner._control._tanks_controller.boosting
    assert runner._control.mode.is_boosting_idle
    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_boosting.flow.value == approx(0.0, abs=0.1)
