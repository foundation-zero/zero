import pytest
from loads.control.stub import PCanStub
import socket
from loads.control.stub.can_frame import CAN_Frame
from loads.config import Settings

settings = Settings()  # type: ignore


@pytest.mark.timeout(1)
async def test_receive_message(settings):
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind((settings.canbus_ip, settings.canbus_port))

    async with PCanStub.init_from_settings(settings) as stub:
        can_msg = await stub.create_can_msg(
            id=12341234, data=b"\x01\x02\x03\x04\x00\x00\x00\x00"
        )

        await stub.send_message(can_msg)

        result, adress = UDPServerSocket.recvfrom(settings.canbus_buffer_size)

        frame = CAN_Frame.parse(result)

        assert frame is not None
        assert frame.can_identifier == 12341234
        assert frame.data == b"\x01\x02\x03\x04\x00\x00\x00\x00"
