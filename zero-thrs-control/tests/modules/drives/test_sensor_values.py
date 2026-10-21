from thrs.input_output.base import Stamped
from thrs.input_output.definitions import sensor
from thrs.input_output.modules.drives import combine_shore_power_converters


def _converter(
    active: bool, igbt_temperatures: tuple[float, float], power: float
) -> sensor.ShorePowerConverter:
    return sensor.ShorePowerConverter(
        active=Stamped.stamp(active),
        esi_transformer_temperature=Stamped.stamp(igbt_temperatures[1] - 2),
        esi_igbt_min_temperature=Stamped.stamp(igbt_temperatures[0]),
        esi_igbt_max_temperature=Stamped.stamp(igbt_temperatures[1]),
        power=Stamped.stamp(power),
    )


def test_combine_shore_power_converters():
    shorepower = combine_shore_power_converters(
        (
            _converter(True, (34.7, 38.2), 16_200),
            _converter(False, (0, 0), 0),
            _converter(True, (30.2, 67.5), 51_400),
        )
    )

    assert shorepower.active.value
    assert shorepower.esi_transformer_temperature.value == 65.5
    assert shorepower.esi_igbt_min_temperature.value == 0
    assert shorepower.esi_igbt_max_temperature.value == 67.5
    assert shorepower.power.value == 67_600
