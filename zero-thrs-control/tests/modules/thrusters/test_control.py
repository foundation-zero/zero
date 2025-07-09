from pytest import approx

from control.modules.thrusters import ThrustersControl
from input_output.base import Stamped
from input_output.definitions.control import Valve
from orchestration.executor import SimulationExecutor
from tests.modules.thrusters.conftest import ThrustersSimulationExecutor


async def test_idle(control: ThrustersControl, executor: SimulationExecutor):
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)
    executor._simulation_inputs.thrusters_fwd.heat_flow = Stamped.stamp(0)


    result = await executor.tick(control.initial(executor.time()).values)
    control.to_idle(result.sensor_values)  # type: ignore

    for i in range(90):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    assert result.simulation_outputs.thrusters_module_supply.flow.value == approx(
        0, abs=0.1
    )  # type: ignore


async def test_cooling(
    control: ThrustersControl, executor: ThrustersSimulationExecutor
):
    result = await executor.tick(control.initial(executor.time()).values)

    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize 10s
    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert result.sensor_values.thrusters_flow_recovery_fwd.flow.value == approx(
        0, abs=1e-2
    )
    assert result.sensor_values.thrusters_flow_recovery_aft.flow.value == approx(
        0, abs=1e-2
    )

    assert isinstance(
        result.simulation_outputs.thrusters_module_supply.flow.value, float
    )
    assert result.simulation_outputs.thrusters_module_supply.flow.value == approx(
        0, abs=1e-2
    )

    assert isinstance(
        result.simulation_outputs.thrusters_module_return.flow.value, float
    )
    assert result.simulation_outputs.thrusters_module_return.flow.value == approx(
        0, abs=1e-2
    )

    assert isinstance(
        result.simulation_inputs.thrusters_seawater_supply.temperature.value, float
    )
    assert isinstance(
        result.simulation_outputs.thrusters_seawater_return.temperature.value, float
    )
    assert (
        result.simulation_inputs.thrusters_seawater_supply.temperature.value
        < result.simulation_outputs.thrusters_seawater_return.temperature.value
    )


async def test_recovery(control: ThrustersControl, executor: SimulationExecutor):
    result = await executor.tick(control.initial(executor.time()).values)

    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize 10s
    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert result.simulation_outputs.thrusters_module_return.flow.value == approx(
        result.simulation_outputs.thrusters_module_supply.flow.value, abs=1e-2
    )

    assert (
        result.sensor_values.thrusters_flow_recovery_fwd.flow.value
        + result.sensor_values.thrusters_flow_recovery_aft.flow.value
        == approx(
            result.simulation_outputs.thrusters_module_return.flow.value, abs=1e-2
        )
    )

    assert (
        result.simulation_outputs.thrusters_module_return.temperature.value
        > result.simulation_inputs.thrusters_module_supply.temperature.value
    )


async def test_recovery_mixing_cold(
    control: ThrustersControl, executor: SimulationExecutor
):
    executor._simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(20)

    result = await executor.tick(control.initial(executor.time()).values)

    # set valves and stabilize 10s
    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value < 50:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value < 50:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

    for i in range(20 * 60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(
            control_values,
        )

        assert (
            result.sensor_values.thrusters_temperature_aft_return.temperature.value > 45
        )
        assert (
            result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 45
        )
        assert control.mode == "recovery"

async def test_recovery_mixing_hot(
    control: ThrustersControl, executor: SimulationExecutor
):
    executor._simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(70)

    result = await executor.tick(control.initial(executor.time()).values)

    # set valves and stabilize 20m
    for i in range(90 + 20 * 60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value > 65:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_A_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 65:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_A_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value < 55:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value < 55:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-2
            )

    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        == approx(70, abs=0.2)
    )
    assert control.mode == "recovery"


async def test_heat_dump_with_cold_sea(
    control: ThrustersControl, executor: SimulationExecutor
):
    executor._simulation_inputs.thrusters_seawater_supply.temperature = Stamped.stamp(
        10
    )

    result = await executor.tick(control.initial(executor.time()).values)
    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize 2m
    for i in range(210):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(30):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert (
            result.sensor_values.thrusters_temperature_supply.temperature.value
            == approx(38, abs=1)
        )


async def test_heat_dump_with_hot_sea(
    control: ThrustersControl, executor: SimulationExecutor
):
    executor._simulation_inputs.thrusters_seawater_supply.temperature = Stamped.stamp(
        45
    )

    result = await executor.tick(control.initial(executor.time()).values)
    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize 10s
    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(30):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert (
            result.sensor_values.thrusters_mix_exchanger.position_rel.value
            == approx(Valve.MIXING_A_TO_AB)
        )


async def test_pump_flow_recovery(
    control: ThrustersControl, executor: SimulationExecutor
):

    result = await executor.tick(control.initial(executor.time()).values)
    # set valves and stabilize 10s
    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(10, abs=1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(10, abs=1)

    executor._simulation_inputs.thrusters_aft.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)

    # set valves and stabilize 30s
    for i in range(120):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(10, abs=1)

    executor._simulation_inputs.thrusters_fwd.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_fwd.heat_flow = Stamped.stamp(0)

    # set valves and stabilize 30s
    for i in range(120):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(0, abs=0.1)


async def test_pump_flow_cooling(
    control: ThrustersControl, executor: SimulationExecutor
):
    result = await executor.tick(control.initial(executor.time()).values)

    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize 10s
    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(22, abs=1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=1)

    executor._simulation_inputs.thrusters_aft.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)

    # set valves and stabilize 30s
    for i in range(120):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=1)

    executor._simulation_inputs.thrusters_fwd.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_fwd.heat_flow = Stamped.stamp(0)

    # set valves and stabilize 30s
    for i in range(120):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(0, abs=0.1)


async def test_pump_flow_safe(control: ThrustersControl, executor: SimulationExecutor):
    result = await executor.tick(control.initial(executor.time()).values)

    control.to_safe(result.sensor_values)  # type: ignore
    # set valves and stabilize 10s
    for i in range(100):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(22, abs=1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=1)

    executor._simulation_inputs.thrusters_aft.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)

    # set valves and stabilize 30s
    for i in range(120):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(22, abs=1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=1)

    executor._simulation_inputs.thrusters_fwd.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_fwd.heat_flow = Stamped.stamp(0)

    # set valves and stabilize 30s
    for i in range(120):
        control_values = control.control(result.sensor_values, executor.time()).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(22, abs=1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(22, abs=1)
