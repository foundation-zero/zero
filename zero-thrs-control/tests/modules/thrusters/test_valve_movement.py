from datetime import datetime, timedelta

from pytest import approx

from thrs.input_output.modules.thrusters import (
    ThrustersSensorValues,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation


async def test_valve_movement(fmu, control, simulation_inputs):
    simulation = Simulation(
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
        fmu,
        simulation_inputs,
        datetime.now(),
        timedelta(seconds=45),
    )

    control_values = control.initial().values

    result = await simulation.tick(control_values)

    control_values.thrusters_shutoff_recovery.setpoint.value = 0

    result = await simulation.tick(control_values)

    assert control_values.thrusters_shutoff_recovery.setpoint.value == 0
    assert result.sensor_values.thrusters_shutoff_recovery.position_rel.value == approx(
        0.5, abs=0.01
    )

    result = await simulation.tick(control_values)

    assert control_values.thrusters_shutoff_recovery.setpoint.value == 0
    assert result.sensor_values.thrusters_shutoff_recovery.position_rel.value == approx(
        0, abs=0.01
    )
