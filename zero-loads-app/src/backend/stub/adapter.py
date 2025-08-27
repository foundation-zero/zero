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
        messages = []
        while True:
            try:
                await self._read_message()
            except BlockingIOError:
                # no more packets waiting
                break
        return messages

    async def read_construct(self):
        messages = []
        while True:
            try:
                await self._read_message_construct()
            except BlockingIOError:
                # no more packets waiting
                break
        return messages

    async def _read_message(self):
        message, address = self.socket.recvfrom(self.bufferSize)
        clientMsg = "Data from Gateway:{}".format(message)
        clientIP = "Gateway IP Address:{}".format(address[0])
        clientPort = "Port:{}".format(address[1])
        logging.info(clientIP + " " + clientPort)
        # call the Package decoder.....
        return await self._decode_can_message(message)

    async def _read_message_construct(self):
        logging.info("Reading message")
        message, address = self.socket.recvfrom(self.bufferSize)
        clientMsg = "Data from Gateway:{}".format(message)
        clientIP = "Gateway IP Address:{}".format(address[0])
        clientPort = "Port:{}".format(address[1])
        logging.info(clientIP + " " + clientPort)
        # call the Package decoder.....
        return await self._decode_can_message_construct(message)

    async def send(self, message):
        logging.info("Sending message")
        # convert message to bytes
        self.socket.sendto(bytes(message), (self.localIP, self.localPort))
        logging.debug("Done")

    @staticmethod
    async def _decode_can_message(message):
        logging.info(f"Message: {message}")
        # Check type of CAN Frame - here done by directly check the single byte of IP Frame
        if message[3] == 0x80:
            logging.debug("CAN 2.0a/b Frame")
        elif message[3] == 0x81:
            logging.debug("CAN 2.0a/b Frame with CRC ")
        elif message[3] == 0x90:
            logging.debug("CAN FD Frame ")
        elif message[3] == 0x91:
            logging.debug("CAN FD Frame with CRC ")
        else:
            logging.debug("no CAN Frame")
            return

        # Get the CAN Msg Flags (Ext. dat Lenght , Bit Rate Switch, Error State Indicator, Ext. ID )
        # here done by converting the 2 bytes to a int Value...Big Endian, unsigned
        CAN_MSG_FLAG = int.from_bytes(
            message[22:24], byteorder="big", signed=False
        )  # Byte 22 and 23
        if CAN_MSG_FLAG & 0x40:
            logging.info("Error State Indicator set")
        if CAN_MSG_FLAG & 0x20:
            logging.info("Bit Rate Switch active ")
        if CAN_MSG_FLAG & 0x10:
            logging.info("Frame use Extended Data Length ")

        # Get the CAN-ID Field (inkl. the MSG Type Info)
        CAN_ID_NUM = int.from_bytes(
            message[24:28], byteorder="big", signed=False
        )  # Byte 24 to 27

        # Get Bit 29 to 31 only  --> RTR / EXT
        CAN_MSG_Type = CAN_ID_NUM & 0xC0000000  # Mask it
        CAN_MSG_Type = CAN_MSG_Type >> 24  # Shift it

        if CAN_MSG_Type & 0x80:
            logging.info("Ext 29 Bit")
        else:
            logging.info("Std 11 Bit")

        if CAN_MSG_Type & 0x40:
            logging.info("RTR")

        # Mask Out the Bit 29 to 31 --> RTR / EXT
        CAN_ID_NUM = CAN_ID_NUM & 0x3FFFFFFF
        logging.info("CAN ID: " + "0x" + "{:x}".format(CAN_ID_NUM) + " ")

        # Get the DLC
        DLC = message[21]  # place of the DLC Information
        logging.info("CAN DLC: " + format(DLC) + " ")

        # using CAN FD DLC is NOT Lengt - convert it first - if less / eq 8 - keep it as it is...!
        LEN = DLC_to_LEN[DLC]
        if (
            LEN > 8
        ):  # only if we use CAN-FD and receive a DLC >8 the D>LC is not the Length
            logging.info("CAN Data Byte counter: " + format(LEN))

        # Loop to all available Data and print (max. 8 DB in a row)
        i = 1
        logging.info("\nData Bytes: ")
        while i <= LEN:
            logging.info(
                "DB["
                + "{:02d}".format(i - 1)
                + "]:"
                + "0x"
                + "{:02X}".format(message[27 + i]),
            )  # 27+1 --> Place of DB0
            if (i % 8) == 0:  # limit to max 8 DB in one row
                logging.info("")
            i = i + 1

        logging.info(
            "\n------------------------------------------------------------------------------\n"
        )

    async def _decode_can_message_construct(self, message: str):
        logging.info("Decoding message")
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
