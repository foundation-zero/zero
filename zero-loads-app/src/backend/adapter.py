import logging
import socket
from contextlib import asynccontextmanager

from aiomqtt import Client as MqttClient
from construct import Container

from .config import Settings
from .stub.can_frame import CAN_Frame, CAN_CRC_Frame, CAN_FD_Frame, CAN_FD_CRC_Frame


class PCanAdapter:
    def __init__(
        self,
        mqtt: MqttClient,
        canbus_ip: str,
        canbus_port: int,
        canbus_buffer_size: int = 1024,
    ):
        self.mqtt = mqtt
        self.ip = canbus_ip
        self.port = canbus_port
        self.buffer_size = canbus_buffer_size

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        UDPServerSocket.bind((canbus_ip, canbus_port))
        self.socket = UDPServerSocket
        logging.info(f"PCanAdapter up and listening on {self.ip}:{self.port}")

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        async with MqttClient(
            settings.mqtt_host, settings.mqtt_port, identifier="loads"
        ) as mqtt_client:
            yield PCanAdapter(
                mqtt_client,
                settings.canbus_ip,
                settings.canbus_port,
                settings.canbus_buffer_size,
            )

    async def run(self):
        """Main run loop to read from the socket and pass messages to MQTT"""
        while True:
            try:
                message = await self._read_message()
                logging.debug(f"Forwarding message to MQTT: {message}")
                await self._send_mqtt_message(message)
            except Exception as e:
                logging.error(e)
                break

    async def _read_message(self):
        """Read a message from the UDP socket and decode it"""
        message, address = self.socket.recvfrom(self.buffer_size)
        logging.debug(f"message: {message} on {address[0]}:{address[1]}")
        return await self._decode_can_frame(message)

    async def _send_mqtt_message(self, message: Container):
        """Send the decoded message to the MQTT broker"""

        can_id = str(message.get("can_identifier"))
        payload = await self._convert_payload(message)

        await self.mqtt.publish(topic=can_id, payload=payload, qos=1)

    async def _convert_payload(self, message: Container):
        """Extract the payload from the message"""
        return int.from_bytes(message.get("payload"), "little")

    @staticmethod
    async def _decode_can_frame(message: bytes):
        """Decode a CAN frame from raw bytes"""
        if message[3] == 0x80:
            logging.debug("CAN 2.0a/b Frame")
            result = CAN_Frame.parse(message)
        elif message[3] == 0x81:
            logging.debug("CAN 2.0a/b Frame with CRC")
            result = CAN_CRC_Frame.parse(message)
        elif message[3] == 0x90:
            logging.debug("CAN FD Frame")
            result = CAN_FD_Frame.parse(message)
        elif message[3] == 0x91:
            logging.debug("CAN FD Frame with CRC")
            result = CAN_FD_CRC_Frame.parse(message)
        else:
            logging.info("Not a valid CAN Frame type")
            result = None
        return result
