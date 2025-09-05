import pytest
import socket
import asyncio
from backend.adapter import PCanAdapter
from pytest import fixture
from backend.config import Settings


@fixture
def settings():
    return Settings(
        mqtt_host="localhost",
        mqtt_port=1883,
        canbus_ip="127.0.0.1",
        canbus_port=56001,
        canbus_buffer_size=1024,
    )


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_receive_message(settings):
    # Prepare a valid CAN_Frame message (0x80)
    frame_bytes = (
        b"\x00\x18"  # length = 24
        b"\x00\x80"  # message_type = 0x80
        + b"TAG12345"  # tag (8 bytes)
        + b"\x00\x00\x00\x01"  # ts_low
        + b"\x00\x00\x00\x02"  # ts_high
        + b"\x01"  # channel
        + b"\x04"  # dlc
        + b"\x00\x02"  # flags (extended)
        + b"\x11\x22\x33\x41"  # can_id
        + b"\x01\x02\x03\x04\x00\x00\x00\x00"  # data (4 bytes valid)
    )

    # Send the UDP message in the background
    def send_udp():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(frame_bytes, (settings.canbus_ip, settings.canbus_port))

    async with PCanAdapter.init_from_settings(settings) as adapter:
        # Run the send_udp function in the background
        asyncio.create_task(asyncio.to_thread(send_udp))
        # Allow some time for the message to be sent and processed
        await asyncio.sleep(0.2)
        result = await adapter._read_message()

        assert result is not None
        assert result.message_type == 0x80
        assert result.dlc == 4
        assert result.payload == b"\x01\x02\x03\x04"
        assert result.can_identifier == 35931752
