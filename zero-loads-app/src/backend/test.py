import asyncio
import logging
from stub.adapter import PCanAdapter
from stub.can_frame import (
    ClassicCAN_IPFrame,
)


logging.basicConfig(level=logging.DEBUG)

adapter = PCanAdapter(localIP="127.0.0.1", localPort=55001)


async def run():
    print("read")
    messages_construct = asyncio.create_task(adapter.read_construct())

    print("send")
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

    print(msg.hex())
    await adapter.send(msg)

    print("Read messages (construct):", messages_construct)


async def main():
    # await asyncio.gather(read(), send())
    await asyncio.gather(run())


asyncio.run(main())
