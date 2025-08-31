import socket
from .can_frame import (
    CANFD_IPFrame,
    ClassicCAN_CRC_IPFrame,
    ClassicCAN_IPFrame,
    CANFD_CRC_IPFrame,
)


class PCanStub:
    def __init__(self, ip: str, port: int, bufferSize: int = 1024):
        self.ip = ip
        self.port = port
        self.bufferSize = bufferSize

    def send(self, msg: bytes):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(msg, (self.ip, self.port))

    def _create_can_msg(self, id: bytes, data: bytes) -> bytes:
        # TODO: Data check input
        # TODO CRC?
        # TODO: length calculation?
        # TODO: timestamp
        msg = ClassicCAN_IPFrame.build(
            {
                "length": 16,
                "message_type": 0x80,
                "tag": b"not_used",
                "ts_low": 12345678,
                "ts_high": 87654321,
                "channel": 1,
                "dlc": len(data),
                "flags": {"RTR": False, "EXTENDED": True},
                "can_id": {
                    "id": 0x1FFFFFFF,
                    "reserved0": 0x00,
                    "rtr": False,
                    "extended": True,
                },
                "data": data,
            }
        )
        return msg

    def _create_can_crc_msg(self, data: bytes) -> bytes:
        msg = ClassicCAN_CRC_IPFrame.build(
            {
                "length": 16,
                "message_type": 0x81,
                "tag": b"not_used",
                "ts_low": 12345678,
                "ts_high": 87654321,
                "channel": 1,
                "dlc": len(data),
                "flags": {
                    "EXTENDED": True,
                    "EDL": False,
                    "BRS": False,
                    "ESI": False,
                },
                "can_id": {
                    "id": 0x1FFFFFFF,
                    "reserved0": 0x00,
                    "rtr": False,
                    "extended": True,
                },
                "data": data,
                "crc32": 12345678,
            }
        )
        return msg

    def _create_can_fd_msg(self, data) -> bytes:
        msg = CANFD_IPFrame.build(
            {
                "length": 28 + len(data),
                "message_type": 0x90,
                "tag": b"not_used",
                "ts_low": 12345678,
                "ts_high": 87654321,
                "channel": 1,
                "dlc": len(data),
                "flags": {"RTR": False, "EXTENDED": True},
                "can_id": {
                    "id": 0x1FFFFFFF,
                    "reserved0": 0x00,
                    "rtr": False,
                    "extended": True,
                },
                "data": data,
            }
        )
        return msg

    def _create_can_fd_crc_msg(self, data: bytes) -> bytes:
        msg = CANFD_CRC_IPFrame.build(
            {
                "length": 16,
                "message_type": 0x91,
                "tag": b"not_used",
                "ts_low": 12345678,
                "ts_high": 87654321,
                "channel": 1,
                "dlc": len(data),
                "flags": {"RTR": False, "EXTENDED": True},
                "can_id": {
                    "id": 0x1FFFFFFF,
                    "reserved0": 0x00,
                    "rtr": False,
                    "extended": True,
                },
                "data": data,
                "crc32": 12345678,
            }
        )
        return msg
