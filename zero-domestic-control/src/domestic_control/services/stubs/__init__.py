from asyncio import TaskGroup
from contextlib import asynccontextmanager
from typing import NamedTuple

from aiomqtt import Client as MqttClient

from domestic_control.config import Settings
from domestic_control.services.stubs.ac import AcStub
from domestic_control.services.stubs.av import AvStub
from domestic_control.services.stubs.ventilation import VentilationStub


class ServiceSettings(NamedTuple):
    host: str
    port: int


class Stub:
    """Main stub class for the domestic control system delegating to various substubs"""

    def __init__(
        self,
        mqtt_client: MqttClient,
        air_conditioning_settings: ServiceSettings,
        ventilation_settings: ServiceSettings,
    ):
        self._av_stub = AvStub(mqtt_client)
        self._ac_stub = AcStub(
            host=air_conditioning_settings.host, port=air_conditioning_settings.port
        )
        self._ventilation_stub = VentilationStub(
            host=ventilation_settings.host, port=ventilation_settings.port
        )

    async def run(self):
        async with TaskGroup() as tg:
            tg.create_task(await self._av_stub.run())
            tg.create_task(self._ac_stub.run())
            tg.create_task(self._ventilation_stub.run())

    @staticmethod
    @asynccontextmanager
    async def from_settings(settings: Settings):
        async with MqttClient(settings.mqtt_host) as mqtt_client:
            yield Stub(
                mqtt_client,
                ServiceSettings(
                    settings.air_conditioning_host, settings.air_conditioning_port
                ),
                ServiceSettings(settings.ventilation_host, settings.ventilation_port),
            )
