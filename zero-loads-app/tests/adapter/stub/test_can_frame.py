import pytest
from pytest import fixture
from adapter.config import Settings
from adapter.stub.can_frame import (
    CAN_Frame,
    CAN_CRC_Frame,
    CAN_FD_Frame,
    CAN_FD_CRC_Frame,
)


@fixture
def settings():
    return Settings(
        mqtt_host="localhost",
        mqtt_port=1883,
        canbus_ip="127.0.0.1",
        canbus_port=56000,
        canbus_buffer_size=1024,
        jwt_secret="test",
    )


@pytest.mark.timeout(2)
@pytest.mark.asyncio
async def test_can_message_parsing(settings):
    # Extended id = True
    frame_bytes = (
        b"\x00\x18"  # length = 24
        b"\x00\x80"  # message_type = 0x80
        + b"TAG12345"  # tag (8 bytes)
        + b"\x00\x00\x00\x01"  # ts_low
        + b"\x00\x00\x00\x02"  # ts_high
        + b"\x01"  # channel
        + b"\x04"  # dlc
        + b"\x00\x02"  # flags (extended)
        + b"\x05\xe3\x0a\x71"  # can_id
        + b"\x01\x02\x03\x04\x00\x00\x00\x00"  # data (4 bytes valid)
    )

    frame = CAN_Frame.parse(frame_bytes)
    assert frame.length == 24
    assert frame.dlc == 4
    assert frame.payload == b"\x01\x02\x03\x04"
    assert frame.flags.extended == True
    assert frame.can_id.extended == True
    assert frame.can_identifier == 12345678
    assert frame.flags.rtr == False
    assert frame.can_id.rtr == False

    # Extended id = False
    frame_bytes = (
        b"\x00\x18"  # length = 24
        b"\x00\x80"  # message_type = 0x80
        + b"TAG12345"  # tag (8 bytes)
        + b"\x00\x00\x00\x01"  # ts_low
        + b"\x00\x00\x00\x02"  # ts_high
        + b"\x01"  # channel
        + b"\x04"  # dlc
        + b"\x00\x00"  # flags (extended)
        + b"\x05\xe3\x0a\x70"  # can_id
        + b"\x01\x02\x03\x04\x00\x00\x00\x00"  # data (4 bytes valid)
    )
    frame = CAN_Frame.parse(frame_bytes)
    assert frame.flags.extended == False
    assert frame.can_id.extended == False
    assert frame.can_id.id == 12345678
    assert frame.can_identifier == 334
    assert frame.flags.rtr == False
    assert frame.can_id.rtr == False


@pytest.mark.timeout(2)
@pytest.mark.asyncio
async def test_can_crc_message_parsing(settings):
    # Extended id = True
    frame_bytes = (
        b"\x00\x18"  # length = 24
        b"\x00\x81"  # message_type = 0x81
        + b"TAG12345"  # tag (8 bytes)
        + b"\x00\x00\x00\x01"  # ts_low
        + b"\x00\x00\x00\x02"  # ts_high
        + b"\x01"  # channel
        + b"\x04"  # dlc
        + b"\x00\x02"  # flags (extended)
        + b"\x05\xe3\x0a\x71"  # can_id
        + b"\x01\x02\x03\x04\x00\x00\x00\x00"  # data (4 bytes valid)
        + b"\x78\x56\x34\x12"  # CRC32
    )

    frame = CAN_CRC_Frame.parse(frame_bytes)
    assert frame.length == 24
    assert frame.dlc == 4
    assert frame.payload == b"\x01\x02\x03\x04"
    assert frame.flags.extended == True
    assert frame.can_id.extended == True
    assert frame.can_identifier == 12345678
    assert frame.flags.rtr == False
    assert frame.can_id.rtr == False
    assert frame.crc32 == 305419896


@pytest.mark.timeout(2)
@pytest.mark.asyncio
async def test_can_fd_message_parsing(settings):
    # Extended id = True
    frame_bytes = (
        b"\x00\x18"  # length = 24
        b"\x00\x90"  # message_type = 0x81
        + b"TAG12345"  # tag (8 bytes)
        + b"\x00\x00\x00\x01"  # ts_low
        + b"\x00\x00\x00\x02"  # ts_high
        + b"\x01"  # channel
        + b"\x04"  # dlc
        + b"\x00\x02"  # flags (extended)
        + b"\x05\xe3\x0a\x71"  # can_id
        + b"\x01\x02\x03\x04"  # data (4 bytes valid)
        + b"\x78\x56\x34\x12"
    )

    frame = CAN_FD_Frame.parse(frame_bytes)
    assert frame.length == 24
    assert frame.dlc == 4
    assert frame.data == b"\x01\x02\x03\x04"
    assert frame.flags.extended == True
    assert frame.can_id.extended == True
    assert frame.can_identifier == 12345678
    assert frame.flags.extended == True
    assert frame.flags.edl == False
    assert frame.flags.brs == False
    assert frame.flags.esi == False


@pytest.mark.timeout(2)
@pytest.mark.asyncio
async def test_can_fd_crc_message_parsing(settings):
    # Extended id = True
    frame_bytes = (
        b"\x00\x18"  # length = 24
        b"\x00\x91"  # message_type = 0x81
        + b"TAG12345"  # tag (8 bytes)
        + b"\x00\x00\x00\x01"  # ts_low
        + b"\x00\x00\x00\x02"  # ts_high
        + b"\x01"  # channel
        + b"\x04"  # dlc
        + b"\x00\x02"  # flags (extended)
        + b"\x05\xe3\x0a\x71"  # can_id
        + b"\x01\x02\x03\x04"  # data (4 bytes valid)
        + b"\x78\x56\x34\x12"
        + b"\x78\x56\x34\x12"  # CRC32
    )

    frame = CAN_FD_CRC_Frame.parse(frame_bytes)
    assert frame.crc32 == 305419896
