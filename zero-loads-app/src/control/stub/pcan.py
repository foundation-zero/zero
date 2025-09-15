import random
import socket
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from .can_frame import CAN_CRC_Frame, CAN_FD_CRC_Frame, CAN_FD_Frame, CAN_Frame
from ..config import Settings
import logging

logger = logging.getLogger("stub")


class PCanStub:
    def __init__(
        self, ip: str, port: int, bufferSize: int = 1024, send_interval: float = 1.0
    ):
        self.ip = ip
        self.port = port
        self.bufferSize = bufferSize
        self.send_interval = send_interval

        logger.info(f"Running PCanStub on {self.ip}:{self.port}")

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        yield PCanStub(
            settings.canbus_ip,
            settings.canbus_port,
            settings.canbus_buffer_size,
        )

    async def run(self):
        """Main run loop to send mock CAN messages"""
        logger.debug(
            f"Sending mock messages to {self.ip}:{self.port} every {self.send_interval} seconds"
        )
        while True:
            data = bytes([random.getrandbits(8) for _ in range(8)])
            can_msg = await self.create_can_msg(id=1, data=data)
            await self.send_message(can_msg)
            await asyncio.sleep(self.send_interval)

    async def send_message(self, msg: bytes):
        """Send a message to the UDP socket"""
        logger.debug(f"Sending message to {self.ip}:{self.port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(msg, (self.ip, self.port))

    async def create_can_msg(self, id: int, data: bytes) -> bytes:
        """Create a classic CAN message (11-bit or 29-bit ID)"""
        dt_low, dt_high = self._datetime_to_pcan_parts(datetime.now())
        msg = CAN_Frame.build(
            {
                "length": 36,
                "message_type": 0x80,
                "tag": b"not_used",
                "ts_low": dt_low,
                "ts_high": dt_high,
                "channel": 1,
                "dlc": len(data),
                "flags": {"rtr": False, "extended": True},
                "can_id": {
                    "id": id,
                    "reserved0": 0,
                    "rtr": False,
                    "extended": True,
                },
                "data": data,
            }
        )
        return msg

    async def create_can_crc_msg(self, id: bytes, data: bytes) -> bytes:
        """Create a classic CAN message with CRC (11-bit or 29-bit ID)"""
        dt_low, dt_high = self._datetime_to_pcan_parts(datetime.now())
        msg = CAN_CRC_Frame.build(
            {
                "length": 40,
                "message_type": 0x81,
                "tag": b"not_used",
                "ts_low": dt_low,
                "ts_high": dt_high,
                "channel": 1,
                "dlc": len(data),
                "flags": {
                    "extended": True,
                    "edl": False,
                    "brs": False,
                    "esi": False,
                },
                "can_id": {
                    "id": id,
                    "reserved0": 0,
                    "rtr": False,
                    "extended": True,
                },
                "data": data,
                "crc32": 12345678,
            }
        )
        return msg

    async def create_can_fd_msg(self, id: bytes, data: bytes) -> bytes:
        """Create a CAN FD message (11-bit or 29-bit ID)"""
        dt_low, dt_high = self._datetime_to_pcan_parts(datetime.now())
        msg = CAN_FD_Frame.build(
            {
                "length": 28 + len(data),
                "message_type": 0x90,
                "tag": b"not_used",
                "ts_low": dt_low,
                "ts_high": dt_high,
                "channel": 1,
                "dlc": len(data),
                "flags": {"rtr": False, "extended": True},
                "can_id": {
                    "id": id,
                    "reserved0": 0,
                    "rtr": False,
                    "extended": True,
                },
                "data": data,
            }
        )
        return msg

    def create_can_fd_crc_msg(self, id: bytes, data: bytes) -> bytes:
        """Create a CAN FD message with CRC (11-bit or 29-bit ID)"""
        dt_low, dt_high = self._datetime_to_pcan_parts(datetime.now())
        msg = CAN_FD_CRC_Frame.build(
            {
                "length": 32 + len(data),
                "message_type": 0x91,
                "tag": b"not_used",
                "ts_low": dt_low,
                "ts_high": dt_high,
                "channel": 1,
                "dlc": len(data),
                "flags": {"rtr": False, "extended": True},
                "can_id": {
                    "id": id,
                    "reserved0": 0,
                    "rtr": False,
                    "extended": True,
                },
                "data": data,
                "crc32": 12345678,
            }
        )
        return msg

    def _datetime_to_pcan_parts(self, dt: datetime):
        """Convert a datetime to PCAN-style timestamp parts (low, high)."""
        epoch = datetime(1970, 1, 1)

        delta = dt - epoch
        ts_us = int(delta.total_seconds() * 1_000_000)

        low = ts_us & 0xFFFFFFFF  # lower 32 bits
        high = (ts_us >> 32) & 0xFFFFFFFF  # upper 32 bits
        return low, high
