from .stub.pcan import PCanStub
from .logging import setup_logging

setup_logging()

### Only used to test

pcan_stub = PCanStub("127.0.0.1", 55001)


# msg = ClassicCAN_IPFrame.build(
#     {
#         "length": 16,
#         "message_type": 0x80,
#         "tag": b"test_tag",
#         "ts_low": 12345678,
#         "ts_high": 87654321,
#         "channel": 1,
#         "dlc": 4,
#         "flags": {"RTR": False, "EXTENDED": True},
#         "can_id": {
#             "id": 0x1FFFFFFF,
#             "reserved0": 0x00,
#             "rtr": False,
#             "extended": True,
#         },
#         "data": b"\x01\x02\x03\x04\x05\x06\x07\x08",
#     }
# )

# Create a CAN frame (standard 11-bit ID)
msg = pcan_stub.create_can_msg(
    id=0x1FFFFFFF,
    data=b"\x01\x02\x03\x04\x05\x06\x07\x08",
)

pcan_stub.send_message(msg)
