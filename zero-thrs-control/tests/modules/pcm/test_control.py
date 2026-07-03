from pytest import approx

from thrs.control.modules.pcm import PcmControl, PcmControlMode
from thrs.input_output.base import Stamped
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation

type PcmSimulation = Simulation[
    PcmSensorValues,
    PcmControlValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
]


def test_idle(control: PcmControl, simulation: PcmSimulation):
    control._parameters.charging_enabled = False
    control._parameters.supplying_enabled = False

    result = simulation.tick(
        control.control(PcmSensorValues.zero())[0],
    )

    for i in range(100):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module1.flow.value
        + result.sensor_values.pcm_flow_module2.flow.value
        + result.sensor_values.pcm_flow_module3.flow.value
        + result.sensor_values.pcm_flow_module4.flow.value
    )
    assert control.mode == PcmControlMode(mode="idle")
    assert pcm_flow == approx(0.0, abs=0.1)
    assert (
        result.simulation_inputs.pcm_thrusters_supply.flow.value
        == approx(  # TODO: get pvt and thrusters supply
            result.simulation_outputs.pcm_consumers_return.flow.value, abs=0.01
        )
    )  # type: ignore


def test_charging(control: PcmControl, simulation: PcmSimulation):
    result = simulation.tick(
        control.control(PcmSensorValues.zero())[0],
    )

    control.to_charging(result.sensor_values)  # type: ignore

    for i in range(200):
        control_values, _ = control.control(result.sensor_values)

        control_values.pcm_switch_consumers.setpoint.value = 0.4  # close consumers switch partly to force flow past PCM #TODO: implement realistic pressure drop on consumers
        result = simulation.tick(control_values)

    assert (
        result.sensor_values.pcm_switch_charging_supply.position_rel.value
        == result.sensor_values.pcm_switch_charging_return.position_rel.value
        == approx(1.0)
    )

    assert result.simulation_inputs.pcm_thrusters_supply.flow.value == approx(
        result.simulation_outputs.pcm_pvt_return.flow.value, abs=0.1
    )  # type: ignore

    assert result.sensor_values.pcm_flow_module1.flow.value == approx(
        control._parameters.pcm_charge_flow, abs=0.5
    )
    assert result.sensor_values.pcm_flow_module2.flow.value == approx(
        control._parameters.pcm_charge_flow, abs=0.5
    )
    assert result.sensor_values.pcm_flow_module3.flow.value == approx(
        control._parameters.pcm_charge_flow, abs=0.5
    )
    assert result.sensor_values.pcm_flow_module4.flow.value == approx(
        control._parameters.pcm_charge_flow, abs=0.5
    )

    for i in range(100):
        result.sensor_values.pcm_temperature_module1.temperature.value = (
            result.sensor_values.pcm_temperature_producers_return.temperature.value
        )
        result.sensor_values.pcm_temperature_module2.temperature.value = (
            result.sensor_values.pcm_temperature_producers_return.temperature.value
        )
        control_values, _ = control.control(result.sensor_values)
        control_values.pcm_switch_consumers.setpoint.value = 0.4  # close consumers switch partly to force flow past PCM #TODO: implement realistic pressure drop on consumers
        result = simulation.tick(control_values)

    assert result.sensor_values.pcm_flow_module1.flow.value == approx(0, abs=0.1)

    assert result.sensor_values.pcm_flow_module2.flow.value == approx(0, abs=0.1)

    assert result.sensor_values.pcm_flow_module3.flow.value == approx(
        control._parameters.pcm_charge_flow, abs=0.5
    )
    assert result.sensor_values.pcm_flow_module4.flow.value == approx(
        control._parameters.pcm_charge_flow, abs=0.5
    )


def test_supplying(control: PcmControl, simulation: PcmSimulation):
    result = simulation.tick(
        control.control(PcmSensorValues.zero())[0],
    )

    control._parameters.charging_enabled = False
    control.to_supplying(result.sensor_values)  # type: ignore

    for i in range(100):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert (
        result.sensor_values.pcm_switch_charging_supply.position_rel.value
        == result.sensor_values.pcm_switch_charging_return.position_rel.value
        == approx(0.0, abs=0.01)
    )

    pcm_flow = (
        result.sensor_values.pcm_flow_module1.flow.value
        + result.sensor_values.pcm_flow_module2.flow.value
        + result.sensor_values.pcm_flow_module3.flow.value
        + result.sensor_values.pcm_flow_module4.flow.value
    )

    assert result.sensor_values.pcm_switch_discharging.position_rel.value == approx(1.0)
    assert result.sensor_values.pcm_pump.flow.value == approx(pcm_flow, abs=0.1)
    assert (
        result.simulation_inputs.pcm_thrusters_supply.flow.value + pcm_flow
        == approx(result.simulation_outputs.pcm_consumers_return.flow.value, abs=0.1)
    )  # type: ignore
    assert result.simulation_inputs.pcm_thrusters_supply.flow.value == approx(
        result.simulation_outputs.pcm_pvt_return.flow.value, abs=0.1
    )  # type: ignore

    assert pcm_flow == approx(4 * control._parameters.pcm_charge_flow, abs=0.5)

    for i in range(100):
        result.sensor_values.pcm_module1.charged.value = False
        result.sensor_values.pcm_module2.charged.value = False
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module1.flow.value
        + result.sensor_values.pcm_flow_module2.flow.value
        + result.sensor_values.pcm_flow_module3.flow.value
        + result.sensor_values.pcm_flow_module4.flow.value
    )

    assert result.sensor_values.pcm_flow_module1.flow.value == approx(0, abs=0.01)
    assert result.sensor_values.pcm_flow_module2.flow.value == approx(0, abs=0.01)
    assert pcm_flow == approx(2 * control._parameters.pcm_charge_flow, abs=0.5)

    for i in range(100):
        result.sensor_values.pcm_module1.charged.value = False
        result.sensor_values.pcm_module2.charged.value = False
        result.sensor_values.pcm_module3.charged.value = False
        result.sensor_values.pcm_module4.charged.value = False
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    pcm_flow = (
        result.sensor_values.pcm_flow_module1.flow.value
        + result.sensor_values.pcm_flow_module2.flow.value
        + result.sensor_values.pcm_flow_module3.flow.value
        + result.sensor_values.pcm_flow_module4.flow.value
    )

    assert result.sensor_values.pcm_flow_module1.flow.value == approx(0, abs=0.01)
    assert result.sensor_values.pcm_flow_module2.flow.value == approx(0, abs=0.01)
    assert result.sensor_values.pcm_flow_module3.flow.value == approx(0, abs=0.01)
    assert result.sensor_values.pcm_flow_module4.flow.value == approx(0, abs=0.01)
    assert pcm_flow == approx(0, abs=0.01)


def test_mode_switches(control: PcmControl, simulation: PcmSimulation):
    simulation._simulation_inputs.pcm_thrusters_supply.temperature = Stamped.stamp(30)

    control_values, _ = control.control(PcmSensorValues.zero())
    result = simulation.tick(control_values)

    assert control.mode == PcmControlMode(mode="idle")

    for i in range(30):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == PcmControlMode(mode="supplying")

    for i in range(3):
        result.sensor_values.pcm_module1.charged.value = False
        result.sensor_values.pcm_module2.charged.value = False
        result.sensor_values.pcm_module3.charged.value = False
        result.sensor_values.pcm_module4.charged.value = True
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == PcmControlMode(mode="supplying")

    for i in range(3):
        result.sensor_values.pcm_module1.charged.value = False
        result.sensor_values.pcm_module2.charged.value = False
        result.sensor_values.pcm_module3.charged.value = False
        result.sensor_values.pcm_module4.charged.value = False
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == PcmControlMode(mode="idle")

    simulation._simulation_inputs.pcm_thrusters_supply.temperature = Stamped.stamp(80)
    for i in range(10):
        result.sensor_values.pcm_module1.charged.value = False
        result.sensor_values.pcm_module2.charged.value = False
        result.sensor_values.pcm_module3.charged.value = False
        result.sensor_values.pcm_module4.charged.value = False
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == PcmControlMode(mode="charging")

    simulation._simulation_inputs.pcm_thrusters_supply.temperature = Stamped.stamp(30)
    for i in range(30):
        result.sensor_values.pcm_module1.charged.value = False
        result.sensor_values.pcm_module2.charged.value = False
        result.sensor_values.pcm_module3.charged.value = False
        result.sensor_values.pcm_module4.charged.value = False
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert control.mode == PcmControlMode(mode="idle")
