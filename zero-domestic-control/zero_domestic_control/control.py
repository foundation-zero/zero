from asyncio import TaskGroup
from contextlib import asynccontextmanager
from homeassistant_api import WebsocketClient as HassClient
from aiomqtt import Client as MqttClient
from zero_domestic_control.av import AvControl
from zero_domestic_control.hass import HassControl
from zero_domestic_control.mqtt import Mqtt
from zero_domestic_control.config import Settings


class Control:
    def __init__(self, hass: HassClient, mqtt_client: MqttClient, mqtt: Mqtt):
        self._hass_control = HassControl(hass, mqtt)
        self._av_control = AvControl(mqtt_client, mqtt)

    async def run(self):
        async with TaskGroup() as tg:
            tg.create_task(self._hass_control.run())
            tg.create_task(self._av_control.run())

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        with HassClient(
            settings.home_assistant_ws_url, settings.home_assistant_token
        ) as hass:
            async with MqttClient(settings.mqtt_host, 1883) as mqtt_client:
                yield Control(hass, mqtt_client, Mqtt(mqtt_client))
