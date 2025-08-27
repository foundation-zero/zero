from src.backend.stub.adapter import PCanAdapter
from src.backend.stub.can_frame import ClassicCAN_IPFrame
import asyncio


def test_decode_message():
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

    decode = _decode_can_frame(msg)
)
