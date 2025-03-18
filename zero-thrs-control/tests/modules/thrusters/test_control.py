from datetime import datetime, timedelta
from pathlib import Path

from pytest import fixture

from control.modules.thrusters import ThrustersControl, ThrustersSetpoints
from input_output.base import Stamped
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    TemperatureBoundary,
)
from simulation.fmu import Fmu
from simulation.io_mapping import IoMapping

simple_inputs = ThrustersSimulationInputs(
    thrusters_aft=HeatSource(heat_flow=Stamped.stamp(9000)),
    thrusters_fwd=HeatSource(heat_flow=Stamped.stamp(4300)),
    thrusters_seawater_supply=Boundary(
        temperature=Stamped.stamp(10), flow=Stamped.stamp(50)
    ),
    thrusters_module_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
)


@fixture
def thrusters() -> IoMapping:
    return IoMapping(
        Fmu(
            str(
                Path(__file__).resolve().parent.parent
                / "../../simulation/models/thrusters/thruster_moduleV5.fmu"
            ),
            timedelta(seconds=0.1),
        ),
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
    )


@fixture
def thrusters_control() -> ThrustersControl:
    return ThrustersControl(ThrustersSetpoints(cooling_mix_setpoint=40))


def test_simple_cooling(thrusters, thrusters_control):
    time = datetime.now()
    sensor_values, _ = thrusters.tick(
        ThrustersControlValues.zero(), simple_inputs, time, timedelta(seconds=0)
    )

    control_values = thrusters_control.simple_cooling(sensor_values, time)

    sensor_values, simulation_outputs = thrusters.tick(
        control_values, simple_inputs, time, timedelta(seconds=60)
    )

    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_fwd_return.temperature.value
    )

    assert simulation_outputs.thrusters_module_supply.flow.value == 0
    assert simulation_outputs.thrusters_module_return.flow.value == 0
    assert (
        simple_inputs.thrusters_seawater_supply.temperature.value
        < simulation_outputs.thrusters_seawater_return.temperature.value
    )


def test_simple_recovery(thrusters, thrusters_control):
    time = datetime.now()
    sensor_values, _ = thrusters.tick(
        ThrustersControlValues.zero(), simple_inputs, time, timedelta(seconds=0)
    )

    control_values = thrusters_control.simple_recovery(time)

    sensor_values, simulation_outputs = thrusters.tick(
        control_values, simple_inputs, time, timedelta(seconds=300)
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
        == simulation_outputs.thrusters_module_supply.flow.value
        == simulation_outputs.thrusters_module_return.flow.value
    )

    assert simulation_outputs.thrusters_module_supply.flow.value > 10
    assert (
        simulation_outputs.thrusters_module_return.flow.value
        == simulation_outputs.thrusters_module_supply.flow.value
    )
    assert (
        simulation_outputs.thrusters_module_return.temperature.value
        < simple_inputs.thrusters_module_supply.temperature.value
    )
