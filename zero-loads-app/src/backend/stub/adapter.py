import logging
import socket
from .can_frame import (
    ClassicCAN_IPFrame,
    ClassicCAN_CRC_IPFrame,
    CANFD_IPFrame,
    CANFD_CRC_IPFrame,
)


# change for your need
localIP = "192.168.0.2"
localPort = 55001

# buffer for payload in IP Frame
DLC_to_LEN = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]


class PCanAdapter:
    def __init__(self, localIP: str, localPort: int, bufferSize: int = 1024):
        self.localIP = localIP
        self.localPort = localPort
        self.bufferSize = bufferSize

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Bind to address and ip
        UDPServerSocket.bind((localIP, localPort))
        self.socket = UDPServerSocket
        logging.info(f"PCanAdapter up and listening on {localIP}:{localPort}")

    async def read(self):
        logging.debug("Start read")
        messages = []
        while True:
            try:
                await self._read_message()
            except BlockingIOError:
                # no more packets waiting
                break
        logging.debug("Done Reading")
        return messages

    async def _read_message(self):
        message, address = self.socket.recvfrom(self.bufferSize)
        clientMsg = "Data from Gateway:{}".format(message)
        clientIP = "Gateway IP Address:{}".format(address[0])
        clientPort = "Port:{}".format(address[1])
        logging.debug(f"message: {clientMsg} on {clientIP}:{clientPort}")
        return await self._decode_can_frame(message)

    async def send(self, message):
        logging.debug("Sending message")
        # convert message to bytes
        self.socket.sendto(bytes(message), (self.localIP, self.localPort))
        logging.debug("Done")

    @staticmethod
    async def _decode_can_frame(message: str):
        logging.debug("Decoding message")
        if message[3] == 0x80:
            logging.debug("CAN 2.0a/b Frame")
            result = ClassicCAN_IPFrame.parse(message)
        elif message[3] == 0x81:
            logging.debug("CAN 2.0a/b Frame with CRC ")
            result = ClassicCAN_CRC_IPFrame.parse(message)
        elif message[3] == 0x90:
            logging.debug("CAN FD Frame ")
            result = CANFD_IPFrame.parse(message)
        elif message[3] == 0x91:
            logging.debug("CAN FD Frame with CRC ")
            result = CANFD_CRC_IPFrame.parse(message)
        else:
            logging.info("Not a valid CAN Frame type")
            result = None
        logging.debug("Done parsing")
        logging.debug(result)
        return result
