from datetime import UTC, datetime, timedelta

from pytest import approx

from thrs.input_output.modules.thrusters import (
    ThrustersSensorValues,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation


def test_valve_movement(fmu, control, simulation_inputs):
    simulation = Simulation(
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
        fmu,
        simulation_inputs,
        datetime.now(UTC),
        timedelta(seconds=45),
    )

    control_values, _ = control.initial()

    result = simulation.tick(control_values)

    control_values.thrusters_switch_recovery.setpoint.value = 0

    result = simulation.tick(control_values)

    assert control_values.thrusters_switch_recovery.setpoint.value == 0
    assert result.sensor_values.thrusters_switch_recovery.position_rel.value == approx(
        0.5, abs=0.01
    )

    result = simulation.tick(control_values)

    assert control_values.thrusters_switch_recovery.setpoint.value == 0
    assert result.sensor_values.thrusters_switch_recovery.position_rel.value == approx(
        0, abs=0.01
    )
