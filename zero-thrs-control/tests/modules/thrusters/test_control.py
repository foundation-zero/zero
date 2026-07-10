from pytest import approx

from tests.modules.thrusters.conftest import ThrustersSimulation
from thrs.control.modules.thrusters import ThrustersControl, ThrustersControlMode
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.units import PcsMode


def test_idle(control: ThrustersControl, simulation: ThrustersSimulation):
    simulation._simulation_inputs.thrusters_thruster_aft.heat_flow = Stamped.stamp(0)
    simulation._simulation_inputs.thrusters_thruster_fwd.heat_flow = Stamped.stamp(0)
    simulation._simulation_inputs.thrusters_pcs.mode = Stamped.stamp(PcsMode.OFF)

    result = simulation.tick(control.initial()[0])

    for i in range(90):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert result.simulation_outputs.thrusters_pcm_supply.flow.value == approx(
        0, abs=0.1
    )  # type: ignore


def test_cooling(control: ThrustersControl, simulation: ThrustersSimulation):
    result = simulation.tick(control.initial()[0])

    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize
    for i in range(100):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert result.sensor_values.thrusters_temperature_supply.temperature.value
    assert result.sensor_values.thrusters_temperature_aft.temperature.value
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_aft.temperature.value
    )

    assert result.sensor_values.thrusters_temperature_fwd.temperature.value
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_fwd.temperature.value
    )

    assert result.sensor_values.thrusters_flow_recovery.flow.value == approx(
        0, abs=1e-2
    )

    assert isinstance(result.simulation_outputs.thrusters_pcm_supply.flow.value, float)
    assert result.simulation_outputs.thrusters_pcm_supply.flow.value == approx(
        0, abs=1e-2
    )

    assert isinstance(result.simulation_outputs.thrusters_pcm_return.flow.value, float)
    assert result.simulation_outputs.thrusters_pcm_return.flow.value == approx(
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


def test_recovery(control: ThrustersControl, simulation: ThrustersSimulation):
    result = simulation.tick(control.initial()[0])

    control.to_recovery(result.sensor_values)  # type: ignore
    for i in range(200):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_aft.temperature.value
    )
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        < result.sensor_values.thrusters_temperature_fwd.temperature.value
    )

    assert isinstance(result.simulation_outputs.thrusters_pcm_return.flow.value, float)
    assert isinstance(result.simulation_outputs.thrusters_pcm_supply.flow.value, float)
    assert result.simulation_outputs.thrusters_pcm_return.flow.value == approx(
        result.simulation_outputs.thrusters_pcm_supply.flow.value, abs=1e-2
    )

    assert result.sensor_values.thrusters_flow_recovery.flow.value == approx(
        result.simulation_outputs.thrusters_pcm_return.flow.value, abs=1e-2
    )

    assert isinstance(
        result.simulation_outputs.thrusters_pcm_return.temperature.value, float
    )
    assert isinstance(
        result.simulation_inputs.thrusters_pcm_supply.temperature.value, float
    )
    assert (
        result.simulation_outputs.thrusters_pcm_return.temperature.value
        > result.simulation_inputs.thrusters_pcm_supply.temperature.value
    )


def test_recovery_mixing(control: ThrustersControl, simulation: ThrustersSimulation):
    simulation._simulation_inputs.thrusters_pcm_supply.temperature = Stamped.stamp(
        control.parameters.recovery_temperature
    )

    result = simulation.tick(control.initial()[0])

    # during warm-up the mixing valve should be closed
    while (
        result.sensor_values.thrusters_temperature_recovery.temperature.value is None
        or (
            result.sensor_values.thrusters_temperature_recovery.temperature.value
            < control.parameters.warmup_temperature
        )
    ):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert control_values.thrusters_mix_recovery.setpoint.value == approx(
            Valve.MIXING_B_TO_AB,
            abs=1e-1,
        )

    # if both aft and fwd are warm, mixing valves should be open
    for i in range(20):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert control_values.thrusters_mix_recovery.setpoint.value > 0


def test_heat_dump_with_cold_sea(
    control: ThrustersControl, simulation: ThrustersSimulation
):
    simulation._simulation_inputs.thrusters_seawater_supply.temperature = Stamped.stamp(
        10
    )

    result = simulation.tick(control.initial()[0])
    control.to_cooling(result.sensor_values)  # type: ignore
    for i in range(360):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    for i in range(30):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert (
            result.sensor_values.thrusters_temperature_supply.temperature.value
            == approx(38, abs=1)
        )


def test_heat_dump_with_hot_sea(
    control: ThrustersControl, simulation: ThrustersSimulation
):
    simulation._simulation_inputs.thrusters_seawater_supply.temperature = Stamped.stamp(
        45
    )

    result = simulation.tick(control.initial()[0])
    control.to_cooling(result.sensor_values)  # type: ignore
    for i in range(500):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    for i in range(30):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert (
            result.sensor_values.thrusters_mix_exchanger.position_rel.value
            == approx(Valve.MIXING_B_TO_AB, abs=1e-4)
        )


def test_recovery_temperature(
    control: ThrustersControl, simulation: ThrustersSimulation
):
    result = simulation.tick(control.initial()[0])
    # set valves and stabilize
    for i in range(500):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    for i in range(60):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)
        assert control.mode == ThrustersControlMode(mode="recovery")
        assert (
            result.sensor_values.thrusters_temperature_recovery.temperature.value
            == approx(
                control.parameters.recovery_temperature,
                abs=2,  # TODO: tune control to decrease error margin and warm-up time
            )
        )


def test_recovery_single_thruster(
    control: ThrustersControl, simulation: ThrustersSimulation
):
    result = simulation.tick(control.initial()[0])

    simulation._simulation_inputs.thrusters_thruster_aft.active = Stamped.stamp(False)
    simulation._simulation_inputs.thrusters_thruster_aft.heat_flow = Stamped.stamp(0)

    # set valves and stabilize
    for i in range(500):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    for i in range(60):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert (
            result.sensor_values.thrusters_temperature_recovery.temperature.value
            == approx(
                control.parameters.recovery_temperature,
                abs=5,  # TODO: tune control to decrease error margin and warm-up time
            )
        )
        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value > 0


def test_flow_thrusters_off(control: ThrustersControl, simulation: ThrustersSimulation):
    simulation._simulation_inputs.thrusters_thruster_aft.active = Stamped.stamp(False)
    simulation._simulation_inputs.thrusters_thruster_aft.heat_flow = Stamped.stamp(0)
    simulation._simulation_inputs.thrusters_thruster_fwd.active = Stamped.stamp(False)
    simulation._simulation_inputs.thrusters_thruster_fwd.heat_flow = Stamped.stamp(0)

    result = simulation.tick(control.initial()[0])
    # set valves and stabilize
    for i in range(120):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    for i in range(60):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(0, abs=0.1)


def test_flow_cooling(control: ThrustersControl, simulation: ThrustersSimulation):
    result = simulation.tick(control.initial()[0])
    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize
    for i in range(200):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    for i in range(60):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)
        assert control.mode == ThrustersControlMode(mode="cooling")
        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(
            control.parameters.cooling_flow, abs=1
        )
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(
            control.parameters.cooling_flow, abs=1
        )


def test_flow_cooling_single_thruster(
    control: ThrustersControl, simulation: ThrustersSimulation
):
    simulation._simulation_inputs.thrusters_thruster_aft.active = Stamped.stamp(False)
    simulation._simulation_inputs.thrusters_thruster_aft.heat_flow = Stamped.stamp(0)

    result = simulation.tick(control.initial()[0])
    control.to_cooling(result.sensor_values)  # type: ignore
    # set valves and stabilize
    for i in range(200):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

    for i in range(60):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert result.sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
        assert result.sensor_values.thrusters_flow_fwd.flow.value == approx(
            control.parameters.cooling_flow, abs=1
        )


def test_cooldown(control: ThrustersControl, simulation: ThrustersSimulation):
    result = simulation.tick(control.initial()[0])
    control_values, _ = control.control(result.sensor_values)

    # set valves and stabilize
    for i in range(300):
        result = simulation.tick(control_values)
        control_values, _ = control.control(result.sensor_values)

    assert control.mode == ThrustersControlMode(mode="recovery")
    assert control_values.thrusters_mix_recovery.setpoint.value > 0.0

    simulation._simulation_inputs.thrusters_thruster_aft.active = Stamped.stamp(False)
    simulation._simulation_inputs.thrusters_thruster_aft.heat_flow = Stamped.stamp(0)
    simulation._simulation_inputs.thrusters_thruster_fwd.active = Stamped.stamp(False)
    simulation._simulation_inputs.thrusters_thruster_fwd.heat_flow = Stamped.stamp(0)
    simulation._simulation_inputs.thrusters_pcs.mode = Stamped.stamp(PcsMode.OFF)

    result = simulation.tick(control_values)
    control_values, _ = control.control(result.sensor_values)

    assert control.mode == ThrustersControlMode(mode="cooldown")
    while control.mode == ThrustersControlMode(mode="cooldown"):
        control_values, _ = control.control(result.sensor_values)
        result = simulation.tick(control_values)

        assert (
            control_values.thrusters_mix_recovery.setpoint.value == Valve.MIXING_B_TO_AB
        )
        assert control._flow_balance_controller.get_setpoints() == [
            control.parameters.cooling_flow,
            control.parameters.cooling_flow,
        ]

    assert control.mode == ThrustersControlMode(mode="idle")

    assert (
        result.sensor_values.thrusters_temperature_aft.temperature.value
        < control.parameters.cooling_temperature
    )
    assert (
        result.sensor_values.thrusters_temperature_fwd.temperature.value
        < control.parameters.cooling_temperature
    )

    assert control_values.thrusters_pump1.dutypoint.value == 0.0
