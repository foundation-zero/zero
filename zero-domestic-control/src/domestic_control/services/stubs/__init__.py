from asyncio import TaskGroup
from contextlib import asynccontextmanager
from domestic_control.config import Settings
from aiomqtt import Client as MqttClient

from domestic_control.services.stubs.ac import AcStub
from domestic_control.services.stubs.av import AvStub
from domestic_control.services.stubs.ventilation import VentilationStub


class Stub:
    """Main stub class for the domestic control system delegating to various substubs"""

    def __init__(
        self,
        mqtt_client: MqttClient,
        air_conditioning_settings: tuple[str, int],
        ventilation_settings: tuple[str, int],
    ):
        self._av_stub = AvStub(mqtt_client)
        self._ac_stub = AcStub(
            host=air_conditioning_settings[0], port=air_conditioning_settings[1]
        )
        self._ventilation_stub = VentilationStub(
            host=ventilation_settings[0], port=ventilation_settings[1]
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
                (settings.air_conditioning_host, settings.air_conditioning_port),
                (settings.ventilation_host, settings.ventilation_port),
            )
