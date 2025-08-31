import logging
import socket
from stub.can_frame import (
    ClassicCAN_IPFrame,
    ClassicCAN_CRC_IPFrame,
    CANFD_IPFrame,
    CANFD_CRC_IPFrame,
)
from aiomqtt import Client as MqttClient
from .config import Settings
from contextlib import asynccontextmanager
import json


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
        logging.debug("Start read")
        while True:
            try:
                message = await self._read_message()
                await self._send_mqtt_message(message)
            except Exception as e:
                logging.error(e)
                break

    async def _read_message(self) -> str:
        message, address = self.socket.recvfrom(self.buffer_size)
        clientMsg = "Data from Gateway:{}".format(message)
        clientIP = "Gateway IP Address:{}".format(address[0])
        clientPort = "Port:{}".format(address[1])
        logging.debug(f"message: {clientMsg} on {clientIP}:{clientPort}")
        return await self._decode_can_frame(message)

    async def _send_mqtt_message(self, message: str):
        message_json = json.loads(message)
        payload = message_json.get("payload")
        topic = message_json.get("can_id")
        await self.mqtt.publish(topic, payload, qos=1)

    @staticmethod
    async def _decode_can_frame(message: bytes) -> str:
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
        return str(result)
