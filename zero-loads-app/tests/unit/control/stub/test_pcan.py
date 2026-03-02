import socket

import pytest

from loads.config import Settings
from loads.control.stub import CAN_Frame, PCanStub


@pytest.mark.timeout(1)
async def test_receive_message(settings: Settings):
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind(("127.0.0.1", 55001))

    async with PCanStub.init_from_settings(
        settings, canbus_ip="127.0.0.1", canbus_port=55001, canbus_buffer_size=1024
    ) as stub:
        can_msg = await stub.create_can_msg(
            id=12341234, data=b"\x01\x02\x03\x04\x00\x00\x00\x00"
        )

        await stub.send_message(can_msg)

        result, address = UDPServerSocket.recvfrom(1024)

        frame = CAN_Frame.parse(result)

        assert frame is not None
        assert frame.can_identifier == 12341234
        assert frame.data == b"\x01\x02\x03\x04\x00\x00\x00\x00"
