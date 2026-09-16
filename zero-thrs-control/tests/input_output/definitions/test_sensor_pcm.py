from thrs.input_output.base import Stamped
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION
from thrs.input_output.modules.pcm import PcmSensorValues

FLOW = 5.0


def _pcm(supply: float, module: float, flow: float = FLOW) -> sensor.Pcm:
    return sensor.Pcm.from_sensors(
        temperature_supply=Stamped.stamp(supply),
        temperature_return=Stamped.stamp(module),
        flow=Stamped.stamp(flow),
        heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        charged=Stamped.stamp(True),
    )


def test_heat_in_watts():
    pcm = _pcm(supply=70.0, module=50.0)

    assert pcm.delta_t.value == -20.0
    assert pcm.heat.value == FLOW * -20.0 * WATER_HEAT_TRANSFER_CONVERSION


def test_charging_when_heat_below_negative_deadband():
    assert (
        _pcm(supply=70.0, module=50.0).charging_state.value
        == sensor.PcmChargingState.CHARGING.value
    )


def test_discharging_when_heat_above_deadband():
    assert (
        _pcm(supply=50.0, module=70.0).charging_state.value
        == sensor.PcmChargingState.DISCHARGING.value
    )


def test_idle_within_deadband():
    # ~0.7 W at nominal flow, well within the 100 W deadband
    assert (
        _pcm(supply=70.0, module=70.002).charging_state.value
        == sensor.PcmChargingState.IDLE.value
    )
    assert (
        _pcm(supply=70.0, module=69.998).charging_state.value
        == sensor.PcmChargingState.IDLE.value
    )


def test_idle_at_zero_flow_despite_temperature_difference():
    pcm = _pcm(supply=70.0, module=50.0, flow=0.0)

    assert pcm.heat.value == 0.0
    assert pcm.charging_state.value == sensor.PcmChargingState.IDLE.value


def test_charged_passthrough():
    assert _pcm(supply=70.0, module=50.0).charged.value is True


def test_charged_false_passthrough():
    pcm = sensor.Pcm.from_sensors(
        temperature_supply=Stamped.stamp(70.0),
        temperature_return=Stamped.stamp(50.0),
        flow=Stamped.stamp(FLOW),
        heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        charged=Stamped.stamp(False),
    )

    assert pcm.charged.value is False


def test_module_computed_field_idle_by_default():
    heat_module = PcmSensorValues.zero().pcm_heat_module1

    assert heat_module.heat.value == 0.0
    assert heat_module.charging_state.value == sensor.PcmChargingState.IDLE.value
    assert heat_module.charged.value is False


def test_module_computed_field_charging():
    sensor_values = PcmSensorValues.zero()
    sensor_values.pcm_temperature_producers_return.temperature = Stamped.stamp(70.0)
    sensor_values.pcm_temperature_module1.temperature = Stamped.stamp(50.0)
    sensor_values.pcm_flow_module1.flow = Stamped.stamp(FLOW)

    heat_module = sensor_values.pcm_heat_module1

    assert heat_module.charging_state.value == sensor.PcmChargingState.CHARGING.value
    assert heat_module.heat.value < 0
