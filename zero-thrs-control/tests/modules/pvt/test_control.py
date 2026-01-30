from pytest import approx
from thrs.control.modules.pvt import PvtControlMode
from thrs.control.modules.pvt_group import PvtGroupControlMode
from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.orchestration.executor import SimulationExecutor

type PvtExecutor = SimulationExecutor[
    PvtSensorValues,
    PvtControlValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
]


async def test_idle(control, executor: PvtExecutor):
    executor._simulation_inputs.pvt_main_fwd.heat_flow = Stamped.stamp(0)
    executor._simulation_inputs.pvt_main_aft.heat_flow = Stamped.stamp(0)
    executor._simulation_inputs.pvt_owners.heat_flow = Stamped.stamp(0)

    result = await executor.tick(
        control.control(PvtSensorValues.zero()).values,
    )

    for i in range(30):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert result.simulation_outputs.pvt_module_return.flow.value == approx(0, abs=0.1)  # type: ignore


async def test_recovery(control, executor):
    result = await executor.tick(
        control.control(PvtSensorValues.zero()).values,
    )

    for i in range(13 * 60):  # Need about 13 minutes to reach stable state
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)

    assert control.mode == PvtControlMode(
        aft=PvtGroupControlMode(mode="recovery"),
        fwd=PvtGroupControlMode(mode="recovery"),
        owners=PvtGroupControlMode(mode="recovery"),
    )

    assert (
        result.sensor_values.pvt_temperature_main_aft_return.temperature.value
        == approx(control.parameters.recovery_temperature, abs=1)
    )
    assert (
        result.sensor_values.pvt_temperature_main_fwd_return.temperature.value
        == approx(control.parameters.recovery_temperature, abs=1)
    )
    assert (
        result.sensor_values.pvt_temperature_owners_return.temperature.value
        == approx(control.parameters.recovery_temperature, abs=1)
    )

    assert (
        result.sensor_values.pvt_flow_main_fwd_recovery.flow.value
        + result.sensor_values.pvt_flow_main_aft_recovery.flow.value
        + result.sensor_values.pvt_flow_owners_recovery.flow.value
        == approx(result.simulation_outputs.pvt_module_return.flow.value, abs=1e-5)
    )

    assert result.simulation_outputs.pvt_module_supply.flow.value == approx(
        result.simulation_outputs.pvt_module_return.flow.value, abs=1e-5
    )


async def test_heat_dump(control, executor: PvtExecutor):
    executor._simulation_inputs.pvt_module_supply.temperature = Stamped.stamp(
        control.parameters.maximum_supply_temperature + 5
    )
    executor._simulation_inputs.pvt_seawater_supply.flow = Stamped.stamp(100)
    executor._simulation_inputs.pvt_seawater_supply.temperature = Stamped.stamp(10)

    result = await executor.tick(
        control.control(PvtSensorValues.zero()).values,
    )

    # Create flow to preheat
    while (
        result.sensor_values.pvt_temperature_supply.temperature.value
        <= control.parameters.maximum_supply_temperature
    ):
        control_values = control.control(result.sensor_values).values
        control_values.pvt_mix_main_aft.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_pump_main_aft.on.value = True
        control_values.pvt_pump_main_aft.dutypoint.value = 1

        control_values.pvt_mix_main_fwd.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_pump_main_fwd.on.value = True
        control_values.pvt_pump_main_fwd.dutypoint.value = 1

        control_values.pvt_mix_owners.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.pvt_pump_owners.on.value = True
        control_values.pvt_pump_owners.dutypoint.value = 1
        result = await executor.tick(control_values)

    for i in range(100):
        control_values = control.control(result.sensor_values).values
        result = await executor.tick(control_values)
        assert result.sensor_values.pvt_temperature_supply.temperature.value == approx(
            control._parameters.maximum_supply_temperature, abs=3
        )
