from thrs.input_output.base import Stamped
from thrs.input_output.definitions import sensor
from thrs.input_output.modules.dc import (
    DcSensorValues,
    brightloop_from_converters,
    combine_brightloops,
    combine_ugrids,
)


def _converter(
    active: bool, channel_temperatures: tuple[float, float, float, float], power: float
) -> sensor.BrightloopConverter:
    return sensor.BrightloopConverter(
        active=Stamped.stamp(active),
        cell01_temperature1=Stamped.stamp(channel_temperatures[0]),
        cell01_temperature2=Stamped.stamp(channel_temperatures[1]),
        cell02_temperature1=Stamped.stamp(channel_temperatures[2]),
        cell02_temperature2=Stamped.stamp(channel_temperatures[3]),
        power=Stamped.stamp(power),
    )


def test_brightloop_from_converters():
    brightloop = brightloop_from_converters(
        (
            _converter(False, (30, 30, 31, 31), 0),
            _converter(True, (38, 38, 41, 40), 15_500),
            _converter(True, (0, 0, 0, 0), 17_500),
        )
    )

    assert brightloop.active.value
    assert brightloop.max_channel_temperature.value == 41
    assert brightloop.power.value == 33_000


def test_combine_brightloops():
    brightloops = combine_brightloops(
        (
            sensor.Brightloop(
                active=Stamped.stamp(False),
                max_channel_temperature=Stamped.stamp(31),
                power=Stamped.stamp(0),
            ),
            sensor.Brightloop(
                active=Stamped.stamp(True),
                max_channel_temperature=Stamped.stamp(44),
                power=Stamped.stamp(60_000),
            ),
        )
    )

    assert brightloops.active.value
    assert brightloops.max_channel_temperature.value == 44
    assert brightloops.power.value == 60_000


def test_combine_ugrids():
    ugrids = combine_ugrids(
        (
            sensor.Ugrid(
                active=Stamped.stamp(True),
                temp_power_stage=Stamped.stamp(46),
                power=Stamped.stamp(17_900),
            ),
            sensor.Ugrid(
                active=Stamped.stamp(True),
                temp_power_stage=Stamped.stamp(40),
                power=Stamped.stamp(8_500),
            ),
        )
    )

    assert ugrids.active.value
    assert ugrids.temp_power_stage.value == 46
    assert ugrids.power.value == 26_400


def test_brightloop_converter_parses_mqtt_payload():
    def stamped(value: object) -> dict:
        return {"Value": value, "TimeStamp": "2026-10-20T14:16:28.6058779Z"}

    converter = sensor.BrightloopConverter.model_validate(
        {
            "Running": stamped(True),
            "Cell01Temperature1": stamped(32),
            "Cell01Temperature2": stamped(32),
            "Cell02Temperature1": stamped(33),
            "Cell02Temperature2": stamped(33),
            "PvPower": stamped(3.0285),
        }
    )

    assert converter.active.value
    assert [temperature.value for temperature in converter.channel_temperatures] == [
        32,
        32,
        33,
        33,
    ]
    assert converter.power.value == 3.0285


def test_converters_share_their_brightloop_yard_tag():
    brightloop_yard_tags = {
        name: field.json_schema_extra["yard_tag"]
        for name, field in DcSensorValues.model_computed_fields.items()
        if isinstance(field.json_schema_extra, dict)
        and field.json_schema_extra["component_type"] == "brightloop"
        and field.json_schema_extra["yard_tag"]
    }
    converter_yard_tags = {
        name: field.json_schema_extra["yard_tag"]
        for name, field in DcSensorValues.model_fields.items()
        if isinstance(field.json_schema_extra, dict)
        and field.json_schema_extra["component_type"] == "brightloop_converter"
    }

    assert len(brightloop_yard_tags) == 6
    assert len(converter_yard_tags) == 22
    for converter, yard_tag in converter_yard_tags.items():
        brightloop = converter.rsplit("_converter", 1)[0]
        assert yard_tag == brightloop_yard_tags[brightloop], converter
