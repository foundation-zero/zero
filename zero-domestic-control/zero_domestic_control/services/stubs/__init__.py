from asyncio import TaskGroup
from contextlib import asynccontextmanager
from zero_domestic_control.config import Settings
from aiomqtt import Client as MqttClient

from zero_domestic_control.services.stubs.ac import TermodinamicaStub
from zero_domestic_control.services.stubs.av import AvStub
import logging


class Stub:
    """Main stub class for the domestic control system delegating to various substubs"""

    def __init__(self, mqtt_client: MqttClient, modbus_settings: tuple[str, int]):
        logging.debug(f"Modbus settings: {modbus_settings}")
        self._av_stub = AvStub(mqtt_client)
        self._ac_stub = TermodinamicaStub(
            host=modbus_settings[0], port=modbus_settings[1]
        )

    async def run(self):
        async with TaskGroup() as tg:
            tg.create_task(await self._av_stub.run())
            tg.create_task(self._ac_stub.run())

    @staticmethod
    @asynccontextmanager
    async def from_settings(settings: Settings):
        async with MqttClient(settings.mqtt_host) as mqtt_client:
            yield Stub(
                mqtt_client, (settings.termodinamica_host, settings.termodinamica_port)
            )
