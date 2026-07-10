from asyncio import TaskGroup
from contextlib import asynccontextmanager
from domestic_control.services.ventilation.control import VentilationControl
from domestic_control.services.ventilation.interface import VentilationInterface
from homeassistant_api import WebsocketClient as HassClient
from aiomqtt import Client as MqttClient
from domestic_control.services.ac import AcControl, AcInterface
from domestic_control.services.ac.thrs import Thrs
from domestic_control.services.av import AvControl, Gude
from domestic_control.services.hass import HassControl
from domestic_control.mqtt import ControlReceive, DataCollection
from domestic_control.sink import CompositeSink, PostgresSink, Sink
from domestic_control.config import Settings
from pyModbusTCP.client import ModbusClient
from sqlalchemy.ext.asyncio import create_async_engine


class Control:
    """Main control class for the domestic control system delegating to various subcontrols"""

    def __init__(
        self,
        hass: HassClient,
        data_sink: Sink,
        ac_client: MqttClient,
        ventilation_client: MqttClient,
        av_client: MqttClient,
        ac_modbus_client: ModbusClient,
        ventilation_modbus_client: ModbusClient,
    ):
        self._hass_control = HassControl(hass, data_sink)
        self._av_control = AvControl(Gude(av_client), data_sink)
        self._ac_control = AcControl(
            ControlReceive(ac_client),
            AcInterface(ac_modbus_client),
            Thrs(ac_client),
            data_sink,
        )
        self._ventilation_control = VentilationControl(
            ControlReceive(ventilation_client),
            VentilationInterface(ventilation_modbus_client),
            data_sink,
        )

    async def run(self):
        av_control = await self._av_control.run()
        ac_control = await self._ac_control.run()
        ventilation_control = await self._ventilation_control.run()

        async with TaskGroup() as tg:
            tg.create_task(self._hass_control.run())
            tg.create_task(av_control)
            tg.create_task(ac_control)
            tg.create_task(ventilation_control)

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        with HassClient(
            settings.home_assistant_ws_url, settings.home_assistant_token
        ) as hass:
            async with (
                MqttClient(
                    settings.mqtt_host, settings.mqtt_port, identifier="domestic_ac"
                ) as ac_client,
                MqttClient(
                    settings.mqtt_host,
                    settings.mqtt_port,
                    identifier="domestic_ventilation",
                ) as ventilation_client,
                MqttClient(
                    settings.mqtt_host, settings.mqtt_port, identifier="domestic_av"
                ) as av_client,
                MqttClient(
                    settings.mqtt_host, settings.mqtt_port, identifier="data"
                ) as data_client,
            ):
                sink = CompositeSink(
                    begin_sinks=[PostgresSink(create_async_engine(settings.pg_url))],
                    sinks=[DataCollection(data_client)],
                )
                ac_modbus_client = ModbusClient(
                    host=settings.air_conditioning_host,
                    port=settings.air_conditioning_port,
                    auto_open=True,
                )
                ventilation_modbus_client = ModbusClient(
                    host=settings.ventilation_host,
                    port=settings.ventilation_port,
                    auto_open=True,
                )

                yield Control(
                    hass=hass,
                    data_sink=sink,
                    av_client=av_client,
                    ac_client=ac_client,
                    ventilation_client=ventilation_client,
                    ac_modbus_client=ac_modbus_client,
                    ventilation_modbus_client=ventilation_modbus_client,
                )
