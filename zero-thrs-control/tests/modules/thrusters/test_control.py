from datetime import timedelta

import pytest
from pytest import approx

from tests.modules.thrusters.conftest import ThrustersRunner
from thrs.control.modules.thrusters import (
    RECOVERY_MIX_LOWER_BOUND,
    RECOVERY_MIX_UPPER_BOUND,
    ThrustersControl,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.definitions.simulation import Pcs, Thruster
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.thrusters import ThrustersSimulationInputs

OFF = Thruster(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False))


def _with_thrusters(
    simulation_inputs: ThrustersSimulationInputs,
    pcs_mode: PcsMode | None = None,
    aft: Thruster | None = None,
    fwd: Thruster | None = None,
) -> ThrustersSimulationInputs:
    return simulation_inputs.model_copy(
        update={
            "thrusters_pcs": Pcs(
                mode=Stamped.stamp(pcs_mode)
                if pcs_mode is not None
                else simulation_inputs.thrusters_pcs.mode
            ),
            "thrusters_thruster_aft": aft or simulation_inputs.thrusters_thruster_aft,
            "thrusters_thruster_fwd": fwd or simulation_inputs.thrusters_thruster_fwd,
        }
    )


def _modes(runner: ThrustersRunner) -> list[str]:
    return runner.mode_transitions(lambda mode: mode.mode)


def test_idle(runner: ThrustersRunner, simulation_inputs: ThrustersSimulationInputs):
    runner.update_simulation_inputs(
        _with_thrusters(simulation_inputs, PcsMode.OFF, aft=OFF, fwd=OFF)
    )

    for sensor_values, control_values, _ in runner.ticks_for(timedelta(minutes=2)):
        assert not control_values.thrusters_pump1.on.value
        assert not control_values.thrusters_pump2.on.value
        assert sensor_values.thrusters_flow_recovery.flow.value == approx(0, abs=0.1)

    assert _modes(runner) == ["idle"]


def test_warmup_until_mix_opens(runner: ThrustersRunner, control: ThrustersControl):
    minimum_flow = control.parameters.thrusters_minimum_flow

    def check_warmup(sensor_values, control_values, controller_state):
        if control.mode.is_warmup:
            assert controller_state.thrusters_aft_flow_controller.setpoint.value == (
                minimum_flow
            )
            assert controller_state.thrusters_fwd_flow_controller.setpoint.value == (
                minimum_flow
            )
            assert not (
                controller_state.thrusters_aft_recovery_temperature_controller.enabled.value
            )
            assert not (
                controller_state.thrusters_fwd_recovery_temperature_controller.enabled.value
            )
            recovery_temperature = (
                sensor_values.thrusters_temperature_recovery.temperature.value
            )
            if (
                recovery_temperature is None
                or recovery_temperature < control.parameters.warmup_temperature
            ):
                assert control_values.thrusters_mix_recovery.setpoint.value == approx(
                    Valve.MIXING_B_TO_AB, abs=1e-2
                )

    _, control_values, controller_state = runner.run_until(
        lambda *_: control.mode.is_recovery,
        within=timedelta(minutes=10),
        check=check_warmup,
    )

    assert control_values.thrusters_mix_recovery.setpoint.value > (
        RECOVERY_MIX_UPPER_BOUND
    )
    assert controller_state.thrusters_aft_recovery_temperature_controller.enabled.value
    assert controller_state.thrusters_fwd_recovery_temperature_controller.enabled.value
    assert _modes(runner) == ["idle", "warmup", "recovery"]


def test_recovery_temperature(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
):
    sensor_values, *_ = runner.run_until_stable(
        lambda sensor_values, *_: (
            sensor_values.thrusters_temperature_recovery.temperature.value
            == approx(control.parameters.recovery_temperature, abs=2)
        ),
        stable_for=timedelta(minutes=2),
        within=timedelta(minutes=20),
    )

    assert _modes(runner) == ["idle", "warmup", "recovery"]
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_aft.temperature.value
    )
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_fwd.temperature.value
    )

    simulation_outputs = runner.simulation_outputs
    assert simulation_outputs is not None
    assert simulation_outputs.thrusters_pcm_return.flow.value == approx(
        simulation_outputs.thrusters_pcm_supply.flow.value, abs=1e-2
    )
    assert sensor_values.thrusters_flow_recovery.flow.value == approx(
        simulation_outputs.thrusters_pcm_return.flow.value, abs=1e-2
    )
    assert (
        simulation_outputs.thrusters_pcm_return.temperature.value
        > simulation_inputs.thrusters_pcm_supply.temperature.value
    )


def test_recovery_single_thruster(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
):
    runner.update_simulation_inputs(_with_thrusters(simulation_inputs, aft=OFF))

    sensor_values, *_ = runner.run_until_stable(
        lambda sensor_values, *_: (
            sensor_values.thrusters_temperature_recovery.temperature.value
            == approx(
                control.parameters.recovery_temperature,
                abs=5,  # TODO: tune control to decrease error margin and warm-up time
            )
        ),
        stable_for=timedelta(minutes=2),
        within=timedelta(minutes=20),
    )

    assert control.mode.is_recovery
    assert sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
    assert sensor_values.thrusters_flow_fwd.flow.value > 0


def test_recovery_falls_back_to_warmup(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
):
    runner.run_until(lambda *_: control.mode.is_recovery, within=timedelta(minutes=10))

    runner.update_simulation_inputs(
        _with_thrusters(
            simulation_inputs,
            aft=Thruster(heat_flow=Stamped.stamp(0), active=Stamped.stamp(True)),
            fwd=Thruster(heat_flow=Stamped.stamp(0), active=Stamped.stamp(True)),
        )
    )
    _, control_values, controller_state = runner.run_until(
        lambda *_: control.mode.is_warmup, within=timedelta(minutes=20)
    )

    assert control_values.thrusters_mix_recovery.setpoint.value < (
        RECOVERY_MIX_LOWER_BOUND
    )
    assert controller_state.thrusters_aft_flow_controller.setpoint.value == (
        control.parameters.thrusters_minimum_flow
    )
    assert controller_state.thrusters_fwd_flow_controller.setpoint.value == (
        control.parameters.thrusters_minimum_flow
    )
    assert not (
        controller_state.thrusters_aft_recovery_temperature_controller.enabled.value
    )

    runner.run(60)

    assert _modes(runner) == ["idle", "warmup", "recovery", "warmup"]


def test_flow_thrusters_off(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
):
    runner.update_simulation_inputs(
        _with_thrusters(simulation_inputs, aft=OFF, fwd=OFF)
    )

    runner.run_until_stable(
        lambda sensor_values, *_: (
            sensor_values.thrusters_flow_aft.flow.value == approx(0, abs=0.1)
            and sensor_values.thrusters_flow_fwd.flow.value == approx(0, abs=0.1)
        ),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=5),
    )

    assert control.mode.is_warmup


def test_cooling_dumps_heat_to_seawater(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
):
    runner.update_simulation_inputs(
        _with_thrusters(simulation_inputs, PcsMode.MANEUVERING)
    )

    sensor_values, *_ = runner.run_until_stable(
        lambda sensor_values, *_: (
            sensor_values.thrusters_flow_recovery.flow.value == approx(0, abs=1e-2)
        ),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=5),
    )

    assert _modes(runner) == ["idle", "cooling"]
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_aft.temperature.value
    )
    assert (
        sensor_values.thrusters_temperature_supply.temperature.value
        < sensor_values.thrusters_temperature_fwd.temperature.value
    )

    simulation_outputs = runner.simulation_outputs
    assert simulation_outputs is not None
    assert simulation_outputs.thrusters_pcm_supply.flow.value == approx(0, abs=1e-2)
    assert simulation_outputs.thrusters_pcm_return.flow.value == approx(0, abs=1e-2)
    assert (
        simulation_inputs.thrusters_seawater_supply.temperature.value
        < simulation_outputs.thrusters_seawater_return.temperature.value
    )


@pytest.mark.parametrize(
    ("aft_active", "fwd_active"), [(True, True), (False, True)], ids=["both", "fwd"]
)
def test_flow_cooling(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
    aft_active: bool,
    fwd_active: bool,
):
    runner.update_simulation_inputs(
        _with_thrusters(
            simulation_inputs,
            PcsMode.MANEUVERING,
            aft=None if aft_active else OFF,
            fwd=None if fwd_active else OFF,
        )
    )
    cooling_flow = 20
    control.update_parameters(
        control.parameters.model_copy(update={"cooling_flow": cooling_flow})
    )

    def expected_flow(active: bool) -> float:
        return cooling_flow if active else 0

    runner.run_until_stable(
        lambda sensor_values, *_: (
            sensor_values.thrusters_flow_aft.flow.value
            == approx(expected_flow(aft_active), abs=1)
            and sensor_values.thrusters_flow_fwd.flow.value
            == approx(expected_flow(fwd_active), abs=1)
        ),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=5),
    )

    assert _modes(runner) == ["idle", "cooling"]


def test_heat_dump_with_cold_sea(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
):
    runner.update_simulation_inputs(
        _with_thrusters(
            simulation_inputs.model_copy(
                update={
                    "thrusters_seawater_supply": simulation_inputs.thrusters_seawater_supply.model_copy(
                        update={"temperature": Stamped.stamp(10)}
                    )
                }
            ),
            PcsMode.MANEUVERING,
        )
    )

    runner.run_until_stable(
        lambda sensor_values, *_: (
            sensor_values.thrusters_temperature_supply.temperature.value
            == approx(control.parameters.cooling_temperature, abs=1)
        ),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=10),
    )

    assert _modes(runner) == ["idle", "cooling"]


def test_heat_dump_with_hot_sea(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
):
    runner.update_simulation_inputs(
        _with_thrusters(
            simulation_inputs.model_copy(
                update={
                    "thrusters_seawater_supply": simulation_inputs.thrusters_seawater_supply.model_copy(
                        update={"temperature": Stamped.stamp(45)}
                    )
                }
            ),
            PcsMode.MANEUVERING,
        )
    )

    runner.run_until_stable(
        lambda sensor_values, *_: (
            sensor_values.thrusters_mix_exchanger.position_rel.value
            == approx(Valve.MIXING_B_TO_AB, abs=1e-4)
        ),
        stable_for=timedelta(seconds=30),
        within=timedelta(minutes=10),
    )

    assert _modes(runner) == ["idle", "cooling"]


def test_cooldown(
    runner: ThrustersRunner,
    control: ThrustersControl,
    simulation_inputs: ThrustersSimulationInputs,
):
    control.update_parameters(
        control.parameters.model_copy(update={"cooling_flow": 20})
    )
    runner.run_until(lambda *_: control.mode.is_recovery, within=timedelta(minutes=10))

    runner.update_simulation_inputs(
        _with_thrusters(simulation_inputs, PcsMode.OFF, aft=OFF, fwd=OFF)
    )

    def check_cooldown(_, control_values, controller_state):
        if control.mode.mode == "cooldown":
            assert control_values.thrusters_mix_recovery.setpoint.value == (
                Valve.MIXING_B_TO_AB
            )
            assert controller_state.thrusters_aft_flow_controller.setpoint.value == (
                control.parameters.cooling_flow
            )
            assert controller_state.thrusters_fwd_flow_controller.setpoint.value == (
                control.parameters.cooling_flow
            )

    runner.run_until(
        lambda *_: control.mode.is_idle,
        within=timedelta(minutes=15),
        check=check_cooldown,
    )

    for sensor_values, control_values, _ in runner.ticks_for(timedelta(seconds=30)):
        assert control.mode.is_idle
        assert (
            sensor_values.thrusters_temperature_aft.temperature.value
            < control.parameters.cooling_temperature
        )
        assert (
            sensor_values.thrusters_temperature_fwd.temperature.value
            < control.parameters.cooling_temperature
        )
        assert not control_values.thrusters_pump1.on.value
        assert not control_values.thrusters_pump2.on.value

    assert _modes(runner) == ["idle", "warmup", "recovery", "cooldown", "idle"]
