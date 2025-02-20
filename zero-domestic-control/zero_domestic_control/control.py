from contextlib import asynccontextmanager
from homeassistant_api import WebsocketClient as HassClient
from aiomqtt import Client as MqttClient
from zero_domestic_control.hass import HassControl
from zero_domestic_control.mqtt import Mqtt
from zero_domestic_control.config import Settings


class Control:
    def __init__(self, hass: HassClient, mqtt: Mqtt):
        self._hass_control = HassControl(hass, mqtt)

    async def run(self):
        await self._hass_control.run()

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        with HassClient(
            settings.home_assistant_ws_url, settings.home_assistant_token
        ) as hass:
            async with MqttClient(settings.mqtt_host, 1883) as mqtt_client:
                yield Control(hass, Mqtt(mqtt_client))
