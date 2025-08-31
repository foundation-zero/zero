import logging
from can_frame import (
    ClassicCAN_IPFrame,
)
import socket

logging.basicConfig(level=logging.DEBUG)

logging.info("send")
# Create a CAN frame (standard 11-bit ID)
msg = ClassicCAN_IPFrame.build(
    {
        "length": 16,
        "message_type": 0x80,
        "tag": b"test_tag",
        "ts_low": 12345678,
        "ts_high": 87654321,
        "channel": 1,
        "dlc": 4,
        "flags": {"RTR": False, "EXTENDED": True},
        "can_id": {
            "id": 0x1FFFFFFF,
            "reserved0": 0x00,
            "rtr": False,
            "extended": True,
        },
        "data": b"\x01\x02\x03\x04\x05\x06\x07\x08",
    }
)

logging.info(type(msg))

# Open a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send to localhost:12000
sock.sendto(msg, ("127.0.0.1", 55001))
