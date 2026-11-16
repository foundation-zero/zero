import re
from collections import Counter

import pytest

from zero_data.device_metadata import (
    DEVICE_METADATA_MACRO,
    Device,
    read_devices,
    render_macro,
)

KEBAB_CASE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


@pytest.fixture(scope="module")
def devices() -> list[Device]:
    return read_devices()


def test_the_macro_is_generated_from_the_csv(devices: list[Device]):
    assert DEVICE_METADATA_MACRO.read_text() == render_macro(devices), (
        "Run `just generate-device-metadata` after editing marpower_device_metadata.csv"
    )


def test_each_topic_is_built_from_its_system_kind_and_technical_name(
    devices: list[Device],
):
    for device in devices:
        levels = (
            [device.system, device.kind]
            if device.kind == device.technical_name
            else [device.system, device.kind, device.technical_name]
        )
        assert device.topic == "/".join(["marpower", *levels])


def test_each_topic_appears_once(devices: list[Device]):
    duplicates = [
        topic
        for topic, count in Counter(device.topic for device in devices).items()
        if count > 1
    ]
    assert duplicates == []


def test_names_are_kebab_case(devices: list[Device]):
    assert [
        device.topic
        for device in devices
        if device.name is not None and not KEBAB_CASE.fullmatch(device.name)
    ] == []


def test_a_name_identifies_one_device_of_a_kind(devices: list[Device]):
    named = Counter(
        (device.system, device.kind, device.name)
        for device in devices
        if device.name is not None
    )
    assert [key for key, count in named.items() if count > 1] == []


def test_render_quotes_values_and_writes_null_for_missing_ones():
    device = Device(
        topic="marpower/45-test/kind/a-1",
        system="45-test",
        kind="kind",
        technical_name="a-1",
        yard_tag=None,
        name="o'clock",
    )
    assert (
        "('1970-01-01 00:00:00', 'marpower/45-test/kind/a-1', '45-test', 'kind', "
        "'a-1', NULL, 'o''clock');"
    ) in render_macro([device])
