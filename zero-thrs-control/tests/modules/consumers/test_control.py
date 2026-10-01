from datetime import timedelta

from pytest import approx

from tests.modules.consumers.conftest import ConsumersRunner
from thrs.control.modules.consumers import ConsumersControl, ConsumersParameters
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)


def _update(control: ConsumersControl, **updates: object) -> None:
    control.update_parameters(
        ConsumersParameters.model_validate(control.parameters.model_dump() | updates)
    )


def _flows(sensor_values: ConsumersSensorValues) -> list[float]:
    return [
        sensor_values.consumers_flow_dhw.flow.value,
        sensor_values.consumers_flow_adsorption.flow.value,
        sensor_values.consumers_flow_bypass.flow.value,
    ]


def _distributed_as(ratios: list[float]):
    """Condition: the flow is split over dhw, adsorption and bypass as `ratios`."""

    def condition(sensor_values: ConsumersSensorValues, *_) -> bool:
        flows = _flows(sensor_values)
        total = sum(flows)
        return total > 1 and [flow / total for flow in flows] == approx(
            ratios, abs=0.02
        )

    return condition


def _switch_setpoints(control_values: ConsumersControlValues) -> list[float]:
    return [
        control_values.consumers_switch_dhw.setpoint.value,
        control_values.consumers_switch_adsorption.setpoint.value,
    ]


def test_flow_follows_the_ratio_setpoints(
    runner: ConsumersRunner, control: ConsumersControl
):
    dhw_ratio = control.parameters.dhw_flow_ratio_setpoint
    adsorption_ratio = control.parameters.adsorption_flow_ratio_setpoint

    _, control_values, _ = runner.run_until_stable(
        _distributed_as(
            [dhw_ratio, adsorption_ratio, 1 - dhw_ratio - adsorption_ratio]
        ),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=10),
    )

    assert _switch_setpoints(control_values) == [Valve.OPEN, Valve.OPEN]


def test_dhw_disabled(runner: ConsumersRunner, control: ConsumersControl):
    _update(control, dhw_enabled=False, adsorption_flow_ratio_setpoint=0.5)

    _, control_values, _ = runner.run_until_stable(
        _distributed_as([0, 0.5, 0.5]),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=10),
    )

    assert _switch_setpoints(control_values) == [Valve.CLOSED, Valve.OPEN]
    assert control_values.consumers_flowcontrol_dhw.setpoint.value == Valve.CLOSED


def test_adsorption_disabled(runner: ConsumersRunner, control: ConsumersControl):
    _update(control, adsorption_enabled=False, dhw_flow_ratio_setpoint=0.5)

    _, control_values, _ = runner.run_until_stable(
        _distributed_as([0.5, 0, 0.5]),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=10),
    )

    assert _switch_setpoints(control_values) == [Valve.OPEN, Valve.CLOSED]
    assert (
        control_values.consumers_flowcontrol_adsorption.setpoint.value == Valve.CLOSED
    )


def test_only_bypass(runner: ConsumersRunner, control: ConsumersControl):
    _update(control, dhw_enabled=False, adsorption_enabled=False)

    sensor_values, control_values, _ = runner.run_until_stable(
        _distributed_as([0, 0, 1]),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=10),
    )

    assert _switch_setpoints(control_values) == [Valve.CLOSED, Valve.CLOSED]
    simulation_outputs = runner.simulation_outputs
    assert simulation_outputs is not None
    assert sensor_values.consumers_flow_bypass.flow.value == approx(
        simulation_outputs.consumers_pcm_return.flow.value, abs=0.1
    )


def test_disabling_dhw_while_running_redistributes_the_flow(
    runner: ConsumersRunner, control: ConsumersControl
):
    dhw_ratio = control.parameters.dhw_flow_ratio_setpoint
    adsorption_ratio = control.parameters.adsorption_flow_ratio_setpoint
    runner.run_until_stable(
        _distributed_as(
            [dhw_ratio, adsorption_ratio, 1 - dhw_ratio - adsorption_ratio]
        ),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=10),
    )

    _update(control, dhw_enabled=False, adsorption_flow_ratio_setpoint=0.5)
    _, control_values, _ = runner.run_until_stable(
        _distributed_as([0, 0.5, 0.5]),
        stable_for=timedelta(minutes=1),
        within=timedelta(minutes=10),
    )

    assert _switch_setpoints(control_values) == [Valve.CLOSED, Valve.OPEN]
