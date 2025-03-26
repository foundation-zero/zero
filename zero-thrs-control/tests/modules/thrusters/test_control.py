from datetime import datetime, timedelta
from pathlib import Path

from pytest import approx, fixture

from control.modules.thrusters import ThrustersControl, ThrustersSetpoints
from input_output.base import Stamped
from input_output.definitions.control import Valve
from input_output.modules.thrusters import (
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    TemperatureBoundary,
)
from orchestration.executor import SimulationExecutor
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping


@fixture
def simulation_inputs():
    return ThrustersSimulationInputs(
        thrusters_aft=HeatSource(heat_flow=Stamped.stamp(9000)),
        thrusters_fwd=HeatSource(heat_flow=Stamped.stamp(4300)),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        thrusters_module_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
    )


@fixture
def io_mapping() -> IoMapping:
    return IoMapping(
        Fmu(
            str(
                Path(__file__).resolve().parent.parent.parent.parent
                / "src/simulation/models/thrusters/thruster_moduleV6.fmu"
            ),
            timedelta(seconds=0.001),
        ),
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
    )


@fixture
def control() -> ThrustersControl:
    return ThrustersControl(
        ThrustersSetpoints(cooling_mix_setpoint=40, recovery_mix_setpoint=60)
    )


def test_simple_cooling(io_mapping, control, simulation_inputs):

    sensor_values, simulation_outputs, _ = io_mapping.tick(
        control.simple_cooling(None, datetime.now()),
        simulation_inputs,
        datetime.now(),
        timedelta(seconds=60),
    )

    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert simulation_outputs.thrusters_module_supply.flow.value == approx(0, abs=1e-3)
    assert simulation_outputs.thrusters_module_return.flow.value == approx(0, abs=1e-3)
    assert (
        simulation_inputs.thrusters_seawater_supply.temperature.value
        < simulation_outputs.thrusters_seawater_return.temperature.value
    )


def test_simple_recovery(io_mapping, control, simulation_inputs):

    sensor_values, simulation_outputs, _ = io_mapping.tick(
        control.simple_recovery(None, datetime.now()),
        simulation_inputs,
        datetime.now(),
        timedelta(seconds=240),
    )

    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_fwd_return.temperature.value
    )
    assert (
        sensor_values.thrusters_flow_aft.flow.value
        + sensor_values.thrusters_flow_fwd.flow.value
        == approx(simulation_outputs.thrusters_module_supply.flow.value, abs=1e-2)
        == approx(simulation_outputs.thrusters_module_return.flow.value, abs=1e-2)
    )

    assert simulation_outputs.thrusters_module_supply.flow.value > 10

    assert (
        simulation_outputs.thrusters_module_return.flow.value
        == simulation_outputs.thrusters_module_supply.flow.value
    )
    assert (
        simulation_outputs.thrusters_module_return.temperature.value
        > simulation_inputs.thrusters_module_supply.temperature.value
    )


async def test_recovery_mixing_cold(io_mapping, control, simulation_inputs):
    simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(20)
    executor = SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=60)
    )
    result = await executor.tick(
        control.simple_recovery(None, datetime.now()),
    )

    # stabilise
    for i in range(2):
        control_values = control.simple_recovery(result.sensor_values, executor.time())
        result = await executor.tick(control_values)

    for i in range(40):
        control_values = control.simple_recovery(result.sensor_values, datetime.now())
        result = await executor.tick(
            control_values,
        )

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value < 50:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-1
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value < 50:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_B_TO_AB, abs=1e-1
            )

    assert result.sensor_values.thrusters_temperature_aft_return.temperature.value > 45
    assert result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 45


async def test_recovery_mixing_hot(io_mapping, control, simulation_inputs):
    simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(20)
    executor = SimulationExecutor(
        io_mapping, simulation_inputs, datetime.now(), timedelta(seconds=60)
    )
    result = await executor.tick(
        control.simple_recovery(None, datetime.now()),
    )

    # stabilise
    for i in range(2):
        control_values = control.simple_recovery(result.sensor_values, executor.time())
        result = await executor.tick(control_values)

    for i in range(40):
        simulation_inputs.thrusters_module_supply.temperature = Stamped.stamp(
            result.sensor_values.thrusters_temperature_fwd_return.temperature.value
        )
        control_values = control.simple_recovery(result.sensor_values, datetime.now())
        result = await executor.tick(
            control_values,
        )

        if result.sensor_values.thrusters_temperature_aft_return.temperature.value > 70:
            assert control_values.thrusters_mix_aft.setpoint.value == approx(
                Valve.MIXING_A_TO_AB, abs=1e-2
            )

        if result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 70:
            assert control_values.thrusters_mix_fwd.setpoint.value == approx(
                Valve.MIXING_A_TO_AB, abs=1e-2
            )

    assert result.sensor_values.thrusters_temperature_aft_return.temperature.value > 70
    assert result.sensor_values.thrusters_temperature_fwd_return.temperature.value > 70
