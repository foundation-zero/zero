from pytest import approx

from thrs.control.modules.boilers import BoilersControl, TanksController
from thrs.input_output.base import Stamped
from thrs.input_output.modules.boilers import BoilersSimulationInputs
from thrs.orchestration.cycler import Cycler
from thrs.orchestration.executor import SimulationExecutionResult


async def test_filling(cycler: Cycler, simulation_inputs: BoilersSimulationInputs):
    result = await cycler.run(60)

    assert isinstance(cycler._control, BoilersControl)
    assert cycler._control._lt1_flow_controller.enabled()
    assert cycler._control._lt2_flow_controller.enabled()

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
    cycler.update_simulation_inputs(simulation_inputs_no_lt1)

    result = await cycler.run(180)

    assert isinstance(cycler._control, BoilersControl)
    assert not cycler._control._lt1_flow_controller.enabled()
    assert cycler._control._lt2_flow_controller.enabled()

    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_lt1.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.boilers_flow_lt2.flow.value > 0.1

    cycler._control.update_parameters(
        cycler._control.parameters.copy(
            update={"maximum_tank_level": 10}
        )  # all tanks full
    )

    result = await cycler.run(180)
    assert isinstance(result, SimulationExecutionResult)
    assert isinstance(cycler._control, BoilersControl) and isinstance(
        cycler._control._tanks_controller, TanksController
    )
    assert not cycler._control._tanks_controller.filling
    assert not cycler._control._lt1_flow_controller.enabled()
    assert not cycler._control._lt2_flow_controller.enabled()

    assert result.sensor_values.boilers_flow_lt1.flow.value == approx(0.0, abs=0.01)
    assert result.sensor_values.boilers_flow_lt2.flow.value == approx(0.0, abs=0.01)


# test filling up to max tank level (no consumption)

# test lt2 filing loop, such that each dt is positive


async def test_boosting_transitions(
    cycler: Cycler, simulation_inputs: BoilersSimulationInputs
):
    # not lt available
    simulation_inputs_no_lt1 = simulation_inputs.model_copy(
        update={
            "boilers_lt1_supply": simulation_inputs.boilers_lt1_supply.model_copy(
                update={"flow": Stamped.stamp(0)}
            )
        }
    )
    cycler.update_simulation_inputs(simulation_inputs_no_lt1)

    # all tanks full
    cycler._control.update_parameters(
        cycler._control.parameters.copy(update={"maximum_tank_level": 10})
    )

    result = await cycler.run(120)

    assert isinstance(cycler._control, BoilersControl) and isinstance(
        cycler._control._tanks_controller, TanksController
    )
    assert cycler._control._tanks_controller.boosting
    assert cycler._control.mode.is_boosting_high_temperature
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
    cycler.update_simulation_inputs(simulation_inputs_no_ht)
    result = await cycler.run(300)

    assert cycler._control._tanks_controller.boosting
    assert cycler._control.mode.is_boosting_heatpump
    assert isinstance(result, SimulationExecutionResult)
    assert result.sensor_values.boilers_flow_boosting.flow.value > 0.1
    assert (
        result.sensor_values.boilers_temperature_boosting_return.temperature.value
        < result.sensor_values.boilers_temperature_boosting_supply.temperature.value
    )
    # TODO: include boosting delta or approximation thereof in assertions...

    # not filling, lt available (switch to lt boosting)
