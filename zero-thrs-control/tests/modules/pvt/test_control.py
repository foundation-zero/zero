from datetime import timedelta

import pytest
from pytest import approx

from tests.modules.pvt.conftest import PvtRunner
from thrs.control.modules.pvt import PvtControl, PvtControlMode
from thrs.control.modules.pvt_group import (
    IDLE_MIX_POSITION,
    RECOVERY_MIX_LOWER_BOUND,
    RECOVERY_MIX_UPPER_BOUND,
    PvtGroupControlMode,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.simulation import Boundary, HeatSource
from thrs.input_output.modules.pvt import PvtSimulationInputs


def _with_heat_flows(
    simulation_inputs: PvtSimulationInputs,
    main_aft: float,
    main_fwd: float,
    owners: float,
) -> PvtSimulationInputs:
    return simulation_inputs.model_copy(
        update={
            "pvt_main_aft": HeatSource(heat_flow=Stamped.stamp(main_aft)),
            "pvt_main_fwd": HeatSource(heat_flow=Stamped.stamp(main_fwd)),
            "pvt_owners": HeatSource(heat_flow=Stamped.stamp(owners)),
        }
    )


def _all_groups(mode: PvtControlMode, group_mode: str) -> bool:
    return all(group.mode == group_mode for group in (mode.aft, mode.fwd, mode.owners))


def _group_mode_transitions(runner: PvtRunner) -> list[list[str]]:
    return [
        runner.mode_transitions(lambda mode: mode.aft.mode),
        runner.mode_transitions(lambda mode: mode.fwd.mode),
        runner.mode_transitions(lambda mode: mode.owners.mode),
    ]


def test_idle(runner: PvtRunner, simulation_inputs: PvtSimulationInputs):
    runner.update_simulation_inputs(_with_heat_flows(simulation_inputs, 0, 0, 0))

    for sensor_values, control_values, _ in runner.ticks_for(timedelta(minutes=2)):
        assert not control_values.pvt_pump_main_aft.on.value
        assert not control_values.pvt_pump_main_fwd.on.value
        assert not control_values.pvt_pump_owners.on.value
        assert sensor_values.pvt_flow_main_aft_recovery.flow.value == approx(0, abs=0.1)
        assert sensor_values.pvt_flow_main_fwd_recovery.flow.value == approx(0, abs=0.1)
        assert sensor_values.pvt_flow_owners_recovery.flow.value == approx(0, abs=0.1)

    assert _group_mode_transitions(runner) == [["idle"]] * 3


def test_idle_mix_position(runner: PvtRunner, control: PvtControl):
    _, control_values, _ = runner.tick()

    assert control.mode.aft == PvtGroupControlMode(mode="idle")
    assert control_values.pvt_mix_main_aft.setpoint.value == IDLE_MIX_POSITION
    assert control_values.pvt_mix_main_fwd.setpoint.value == IDLE_MIX_POSITION
    assert control_values.pvt_mix_owners.setpoint.value == IDLE_MIX_POSITION


@pytest.mark.xfail(
    strict=True,
    reason="PVT FMU wires strings 1-6 to the fwd group and 7-13 to the aft group; "
    "on board strings 1-6 are aft and 7-13 are fwd",
)
def test_groups_follow_their_own_strings(
    runner: PvtRunner,
    control: PvtControl,
    simulation_inputs: PvtSimulationInputs,
):
    runner.update_simulation_inputs(_with_heat_flows(simulation_inputs, 0, 16000, 8000))

    sensor_values, *_ = runner.run_until(
        lambda *_: control.mode.fwd.mode == "warmup", within=timedelta(minutes=5)
    )

    aft_strings = sensor_values.pvt_max_temperature_main_aft_strings.temperature.value
    fwd_strings = sensor_values.pvt_max_temperature_main_fwd_strings.temperature.value
    assert control.mode.aft.mode == "idle"
    assert aft_strings is not None and fwd_strings is not None
    assert aft_strings < fwd_strings


def test_warmup_until_mix_opens(runner: PvtRunner, control: PvtControl):
    def check_warmup(_, control_values, controller_state):
        if control.mode.aft.mode == "warmup":
            assert control_values.pvt_pump_main_aft.on.value
            assert (
                control_values.pvt_pump_main_aft.dutypoint.value
                == control.parameters.main_aft_minimum_pump_dutypoint
            )
            assert not controller_state.pvt_main_aft_pump_controller.enabled.value
            assert controller_state.pvt_main_aft_warmup_mix_controller.enabled.value

    _, control_values, controller_state = runner.run_until(
        lambda *_: control.mode.aft.mode == "recovery",
        within=timedelta(minutes=10),
        check=check_warmup,
    )

    assert control_values.pvt_mix_main_aft.setpoint.value > RECOVERY_MIX_UPPER_BOUND
    assert controller_state.pvt_main_aft_pump_controller.enabled.value
    assert runner.mode_transitions(lambda mode: mode.aft.mode) == [
        "idle",
        "warmup",
        "recovery",
    ]


def test_recovery(runner: PvtRunner, control: PvtControl):
    recovery_temperature = control.parameters.recovery_temperature

    def returns_at_recovery_temperature(sensor_values, *_) -> bool:
        return all(
            temperature == approx(recovery_temperature, abs=1)
            for temperature in (
                sensor_values.pvt_temperature_main_aft_return.temperature.value,
                sensor_values.pvt_temperature_main_fwd_return.temperature.value,
                sensor_values.pvt_temperature_owners_return.temperature.value,
            )
        )

    runner.run_until(
        lambda *_: _all_groups(control.mode, "recovery"),
        within=timedelta(minutes=10),
    )
    sensor_values, *_ = runner.run_until_stable(
        returns_at_recovery_temperature,
        stable_for=timedelta(minutes=2),
        within=timedelta(minutes=30),
    )

    assert _group_mode_transitions(runner) == [["idle", "warmup", "recovery"]] * 3
    simulation_outputs = runner.simulation_outputs
    assert simulation_outputs is not None
    assert (
        sensor_values.pvt_flow_main_fwd_recovery.flow.value
        + sensor_values.pvt_flow_main_aft_recovery.flow.value
        + sensor_values.pvt_flow_owners_recovery.flow.value
        == approx(simulation_outputs.pvt_pcm_return.flow.value, abs=1e-5)
    )
    assert simulation_outputs.pvt_pcm_supply.flow.value == approx(
        simulation_outputs.pvt_pcm_return.flow.value, abs=1e-5
    )


def test_recovery_falls_back_to_warmup(
    runner: PvtRunner,
    control: PvtControl,
    simulation_inputs: PvtSimulationInputs,
):
    runner.run_until(
        lambda *_: _all_groups(control.mode, "recovery"),
        within=timedelta(minutes=10),
    )

    runner.update_simulation_inputs(_with_heat_flows(simulation_inputs, 0, 0, 0))
    _, control_values, controller_state = runner.run_until(
        lambda *_: _all_groups(control.mode, "warmup"),
        within=timedelta(minutes=20),
    )

    assert control_values.pvt_mix_main_aft.setpoint.value < RECOVERY_MIX_LOWER_BOUND
    assert (
        control_values.pvt_pump_main_aft.dutypoint.value
        == control.parameters.main_aft_minimum_pump_dutypoint
    )
    assert not controller_state.pvt_main_aft_pump_controller.enabled.value

    runner.run(60)

    assert (
        _group_mode_transitions(runner)
        == [["idle", "warmup", "recovery", "warmup"]] * 3
    )


# TODO: the strings stay warmer than the return, so idle -> warmup re-triggers on
# the next tick. Needs a better idle -> warmup trigger, and intermittent
# circulation during idle so the string temperatures stay representative.
@pytest.mark.xfail(
    strict=True, reason="Groups chatter between warmup and idle once cooled down"
)
def test_warmup_falls_back_to_idle(
    runner: PvtRunner,
    control: PvtControl,
    simulation_inputs: PvtSimulationInputs,
):
    runner.run_until(
        lambda *_: _all_groups(control.mode, "warmup"),
        within=timedelta(minutes=10),
    )

    # Negative heat flow models the strings losing heat, e.g. at night.
    runner.update_simulation_inputs(
        _with_heat_flows(simulation_inputs, -4000, -4000, -2000)
    )
    runner.run_until(
        lambda *_: _all_groups(control.mode, "idle"),
        within=timedelta(minutes=10),
    )

    for _, control_values, _ in runner.ticks_for(timedelta(minutes=1)):
        assert _all_groups(control.mode, "idle")
        assert control_values.pvt_mix_main_aft.setpoint.value == IDLE_MIX_POSITION
        assert not control_values.pvt_pump_main_aft.on.value

    assert _group_mode_transitions(runner) == [["idle", "warmup", "idle"]] * 3


def test_heat_dump(
    runner: PvtRunner,
    control: PvtControl,
    simulation_inputs: PvtSimulationInputs,
):
    maximum_supply_temperature = control.parameters.maximum_supply_temperature
    runner.update_simulation_inputs(
        simulation_inputs.model_copy(
            update={
                "pvt_pcm_supply": simulation_inputs.pvt_pcm_supply.model_copy(
                    update={
                        "temperature": Stamped.stamp(maximum_supply_temperature + 5)
                    }
                ),
                "pvt_seawater_supply": Boundary(
                    temperature=Stamped.stamp(10), flow=Stamped.stamp(100)
                ),
            }
        )
    )

    def supply_at_maximum(sensor_values, *_) -> bool:
        return sensor_values.pvt_temperature_supply.temperature.value == approx(
            maximum_supply_temperature, abs=3
        )

    runner.run_until(
        lambda *_: _all_groups(control.mode, "recovery"),
        within=timedelta(minutes=10),
    )
    runner.run_until_stable(
        supply_at_maximum,
        stable_for=timedelta(minutes=2),
        within=timedelta(minutes=10),
    )
