from asyncio import TaskGroup
from contextlib import asynccontextmanager
from homeassistant_api import WebsocketClient as HassClient
from aiomqtt import Client as MqttClient
from zero_domestic_control.services.ac import AcControl, TermodinamicaAc
from zero_domestic_control.services.ac.thrs import Thrs
from zero_domestic_control.services.av import AvControl, Gude
from zero_domestic_control.services.hass import HassControl
from zero_domestic_control.mqtt import ControlReceive, DataCollection
from zero_domestic_control.config import Settings
from pyModbusTCP.client import ModbusClient


class Control:
    """Main control class for the domestic control system delegating to various subcontrols"""

    def __init__(
        self,
        hass: HassClient,
        data_client: MqttClient,
        ac_client: MqttClient,
        av_client: MqttClient,
        modbus_client: ModbusClient,
    ):
        data_collection = DataCollection(data_client)
        self._hass_control = HassControl(hass, data_collection)
        self._av_control = AvControl(Gude(av_client), data_collection)
        self._ac_control = AcControl(
            ControlReceive(ac_client),
            TermodinamicaAc(modbus_client),
            Thrs(ac_client),
            data_collection,
        )

    async def run(self):
        async with TaskGroup() as tg:
            tg.create_task(self._hass_control.run())
            tg.create_task(self._av_control.run())
            tg.create_task(self._ac_control.run())

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        with HassClient(
            settings.home_assistant_ws_url, settings.home_assistant_token
        ) as hass:
            async with (
                MqttClient(
                    settings.mqtt_host, 1883, identifier="domestic_ac"
                ) as ac_client,
                MqttClient(
                    settings.mqtt_host, 1883, identifier="domestic_av"
                ) as av_client,
                MqttClient(settings.mqtt_host, 1883, identifier="data") as data_client,
            ):
                modbus_client = ModbusClient(
                    host=settings.termodinamica_host,
                    port=settings.termodinamica_port,
                    auto_open=True,
                )
                yield Control(hass, data_client, av_client, ac_client, modbus_client)
