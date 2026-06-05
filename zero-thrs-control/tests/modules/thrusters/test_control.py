from pytest import approx

from tests.modules.thrusters.conftest import ThrustersSimulationExecutor
from thrs.control.modules.thrusters import ThrustersControl, ThrustersControlMode
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.units import PcsMode
from thrs.orchestration.executor import SimulationExecutor


async def test_idle(control: ThrustersControl, executor: SimulationExecutor):
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)
    executor._simulation_inputs.thrusters_fwd.heat_flow = Stamped.stamp(0)
    executor._simulation_inputs.thrusters_pcs.mode = Stamped.stamp(PcsMode.OFF)

    result = await executor.tick(control.initial().values)

    for i in range(90):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert result.simulation_outputs.thrusters_module_supply.flow.value == approx(
        0, abs=0.1
    )  # type: ignore


async def test_cooling(
    control: ThrustersControl, executor: ThrustersSimulationExecutor
):
    result = await executor.tick(control.initial().values)

    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize
    for i in range(100):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert result.sensor_values.thrusters_temperature_supply.temperature.value
    assert result.sensor_values.thrusters_temperature_aft_return.temperature.value
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_aft_return.temperature.value
    )

    assert result.sensor_values.thrusters_temperature_fwd_return.temperature.value
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert result.sensor_values.thrusters_flow_recovery.flow.value == approx(
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
    result = await executor.tick(control.initial().values)

    control.to_recovery(result.sensor_values)  # type: ignore
    for i in range(200):
        control_values = control.control(result.sensor_values).values
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

    assert result.sensor_values.thrusters_flow_recovery.flow.value == approx(
        result.simulation_outputs.thrusters_module_return.flow.value, abs=1e-2
    )

    assert (
        result.simulation_outputs.thrusters_module_return.temperature.value
        > result.simulation_inputs.thrusters_module_supply.temperature.value
    )


async def test_recovery_mixing(control: ThrustersControl, executor: SimulationExecutor):
    executor._simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(
        control.parameters.recovery_temperature
    )

    result = await executor.tick(control.initial().values)

    # during warm-up the mixing valve should be closed
    while (
        result.sensor_values.thrusters_temperature_recovery.temperature.value is None
        or (
            result.sensor_values.thrusters_temperature_recovery.temperature.value
            < control.parameters.warmup_temperature
        )
    ):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert control_values.thrusters_mix_recovery.setpoint.value == approx(
            Valve.MIXING_B_TO_AB,
            abs=1e-1,
        )

    # if both aft and fwd are warm, mixing valves should be open
    for i in range(20):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert control_values.thrusters_mix_recovery.setpoint.value > 0


async def test_heat_dump_with_cold_sea(
    control: ThrustersControl, executor: SimulationExecutor
):
    executor._simulation_inputs.thrusters_seawater_supply.temperature = Stamped.stamp(
        10
    )

    result = await executor.tick(control.initial().values)
    control.to_cooling(result.sensor_values)  # type: ignore
    for i in range(360):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    for i in range(30):
        control_values = control.control(result.sensor_values).values
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

    result = await executor.tick(control.initial().values)
    control.to_cooling(result.sensor_values)  # type: ignore
    for i in range(500):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    for i in range(30):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert (
            result.sensor_values.thrusters_mix_exchanger.position_rel.value
            == approx(Valve.MIXING_B_TO_AB, abs=1e-4)
        )


async def test_recovery_temperature(
    control: ThrustersControl, executor: SimulationExecutor
):
    result = await executor.tick(control.initial().values)
    # set valves and stabilize
    for i in range(500):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)
        assert control.mode == ThrustersControlMode(mode="recovery")
        assert (
            result.sensor_values.thrusters_temperature_recovery.temperature.value
            == approx(
                control.parameters.recovery_temperature,
                abs=2,  # TODO: tune control to decrease error margin and warm-up time
            )
        )


async def test_recovery_single_thruster(
    control: ThrustersControl, executor: SimulationExecutor
):
    result = await executor.tick(control.initial().values)

    executor._simulation_inputs.thrusters_aft.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)

    # set valves and stabilize
    for i in range(500):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert (
            result.sensor_values.thrusters_temperature_recovery.temperature.value
            == approx(
                control.parameters.recovery_temperature,
                abs=5,  # TODO: tune control to decrease error margin and warm-up time
            )
        )
        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value > 0


async def test_flow_thrusters_off(
    control: ThrustersControl, executor: SimulationExecutor
):
    executor._simulation_inputs.thrusters_aft.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)
    executor._simulation_inputs.thrusters_fwd.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_fwd.heat_flow = Stamped.stamp(0)

    result = await executor.tick(control.initial().values)
    # set valves and stabilize
    for i in range(120):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(0, abs=0.1)


async def test_flow_cooling(control: ThrustersControl, executor: SimulationExecutor):
    result = await executor.tick(control.initial().values)
    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize
    for i in range(200):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)
        assert control.mode == ThrustersControlMode(mode="cooling")
        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(
            control.parameters.cooling_flow, abs=1
        )
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(
            control.parameters.cooling_flow, abs=1
        )


async def test_flow_cooling_single_thruster(
    control: ThrustersControl, executor: SimulationExecutor
):
    executor._simulation_inputs.thrusters_aft.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)

    result = await executor.tick(control.initial().values)
    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize
    for i in range(200):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    for i in range(60):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(
            control.parameters.cooling_flow, abs=1
        )


async def test_cooldown(control: ThrustersControl, executor: SimulationExecutor):
    result = await executor.tick(control.initial().values)
    control_values = control.control(result.sensor_values).values

    # set valves and stabilize
    for i in range(300):
        result = await executor.tick(control_values)
        control_values = control.control(result.sensor_values).values

    assert control.mode == ThrustersControlMode(mode="recovery")
    assert control_values.thrusters_mix_recovery.setpoint.value > 0.0

    executor._simulation_inputs.thrusters_aft.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_aft.heat_flow = Stamped.stamp(0)
    executor._simulation_inputs.thrusters_fwd.active = Stamped.stamp(False)
    executor._simulation_inputs.thrusters_fwd.heat_flow = Stamped.stamp(0)
    executor._simulation_inputs.thrusters_pcs.mode = Stamped.stamp(PcsMode.OFF)

    result = await executor.tick(control_values)
    control_values = control.control(result.sensor_values).values

    assert control.mode == ThrustersControlMode(mode="cooldown")
    while control.mode == ThrustersControlMode(mode="cooldown"):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

        assert (
            control_values.thrusters_mix_recovery.setpoint.value == Valve.MIXING_B_TO_AB
        )
        assert control._flow_balance_controller.get_setpoints() == [
            control.parameters.cooling_flow,
            control.parameters.cooling_flow,
        ]

    assert control.mode == ThrustersControlMode(mode="idle")

    assert (
        result.sensor_values.thrusters_temperature_aft_return.temperature.value
        < control.parameters.cooling_temperature
    )
    assert (
        result.sensor_values.thrusters_temperature_fwd_return.temperature.value
        < control.parameters.cooling_temperature
    )

    assert control_values.thrusters_pump_1.dutypoint.value == 0.0
