from datetime import datetime, timedelta

from pytest import approx
from input_output.modules.pvt import PvtSensorValues


def test_recovery(io_mapping, pvt_control, simulation_inputs):
    pvt_control.to_recovery()
    sensor_values, simulation_outputs, _ = io_mapping.tick(
    pvt_control.control(PvtSensorValues.zero(), datetime.now()).values,
    simulation_inputs,
    datetime.now(),
    timedelta(seconds=240),
)
    assert simulation_outputs.pvt_module_return.flow.value > 0
    assert sensor_values.pvt_flow_main_fwd.flow.value + sensor_values.pvt_flow_main_aft.flow.value + sensor_values.pvt_flow_owners.flow.value == approx(simulation_outputs.pvt_module_return.flow.value, abs = 1e-5)
    assert simulation_outputs.pvt_module_supply.flow.value == approx(simulation_outputs.pvt_module_return.flow.value, abs = 1e-5)
