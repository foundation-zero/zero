import asyncio
import socket
from unittest.mock import AsyncMock

import pytest

from loads.config import Settings
from loads.control import PCanAdapter


@pytest.mark.timeout(2)
async def test_receive_can_message(settings: Settings):
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
        + b"\x05\xe3\x0a\x71"  # can_id
        + b"\x01\x02\x03\x04\x00\x00\x00\x00"  # data (4 bytes valid)
    )

    # Send the UDP message in the background
    def send_udp():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(frame_bytes, ("127.0.0.1", 55001))

    # Mock MQTT client
    class DummyMQTT(AsyncMock):
        async def publish(self, *args, **kwargs):
            return None

    dummy_mqtt = DummyMQTT()

    adapter = PCanAdapter(
        dummy_mqtt,
        "127.0.0.1",
        55001,
        1024,
    )

    asyncio.create_task(asyncio.to_thread(send_udp))
    await asyncio.sleep(0.2)
    result = await adapter._read_message()

    assert result is not None
    assert result.message_type == 0x80
    assert result.dlc == 4
    assert result.payload == b"\x01\x02\x03\x04"
    assert result.can_identifier == 12345678
