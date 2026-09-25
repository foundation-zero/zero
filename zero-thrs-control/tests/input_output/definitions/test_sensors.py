import pytest

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


@pytest.mark.parametrize(
    ("temp_in", "temp_out", "flow", "delta_t", "heat"),
    [
        (10, 10, 10, 0, 0),
        (10, 20, 10, 10, 6973.333333333333),
        (None, None, 0, None, 0),
        (None, None, 10, None, None),
        (10, 20, None, 10, None),
        (10, 10, None, 0, 0),
        (10, None, None, None, None),
        (None, None, None, None, None),
    ],
    ids=(
        "Zero delta",
        "Normal",
        "Delta unknown, zero flow",
        "Delta unknown, normal flow",
        "Delta, flow unknown",
        "Zero delta, flow unknown",
        "Most unknown",
        "All unknown",
    ),
)
def test_heat_transfer_device(temp_in, temp_out, flow, delta_t, heat):
    pcm = sensor.HeatTransferDevice.from_sensors(
        temperature_supply=Stamped.stamp(temp_in),
        temperature_return=Stamped.stamp(temp_out),
        flow=Stamped.stamp(flow),
        heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
        temperature_supply_source="",
        temperature_return_source="",
        flow_source="",
    )

    assert pcm.delta_t.value == delta_t
    assert pcm.heat.value == heat
