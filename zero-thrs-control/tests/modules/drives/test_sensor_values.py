from thrs.input_output.base import Stamped
from thrs.input_output.definitions import sensor


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


def test_shore_power_group_from_converters():
    shorepower = sensor.ShorePowerGroup.from_converters(
        (
            _converter(True, (34.7, 38.2), 16_200),
            _converter(False, (0, 0), 0),
            _converter(True, (30.2, 67.5), 51_400),
        )
    )

    assert shorepower.any_active.value
    assert shorepower.max_esi_transformer_temperature.value == 65.5
    assert shorepower.min_esi_igbt_min_temperature.value == 0
    assert shorepower.max_esi_igbt_max_temperature.value == 67.5
    assert shorepower.total_power.value == 67_600


def test_propulsion_drive_ignores_temperature_while_disabled():
    disabled = sensor.PropulsionDrive(
        active=Stamped.stamp(False),
        temp_power_stage=Stamped.stamp(198),
        power=Stamped.stamp(0),
    )
    enabled = sensor.PropulsionDrive(
        active=Stamped.stamp(True),
        temp_power_stage=Stamped.stamp(52),
        power=Stamped.stamp(120_000),
    )

    assert disabled.temp_power_stage.value is None
    assert enabled.temp_power_stage.value == 52
