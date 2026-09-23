from thrs.input_output.base import Stamped
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION


def test_heat_transfer_device_heat_in_watts():
    pcm = sensor.HeatTransferDevice.from_sensors(
        temperature_supply=Stamped.stamp(70.0),
        temperature_return=Stamped.stamp(50.0),
        flow=Stamped.stamp(5.0),
        heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        temperature_supply_source="",
        temperature_return_source="",
        flow_source="",
    )

    assert pcm.delta_t.value == -20.0
    assert pcm.heat.value == 5.0 * -20.0 * WATER_HEAT_TRANSFER_CONVERSION
