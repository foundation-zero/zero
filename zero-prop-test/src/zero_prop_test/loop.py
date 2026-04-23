from asyncio import TaskGroup, sleep
from contextlib import asynccontextmanager
from datetime import timedelta, datetime
from typing import Any, AsyncGenerator, Sequence

from pydantic import BaseModel

from zero_prop_test.io_link import (
    Client as IoLinkClient,
    IoLinkDevice,
    IoLinkDeviceType,
)
from zero_prop_test.modbus import Address as ModbusAddress
from zero_prop_test.modbus import Client as ModbusClient
from zero_prop_test.settings import MqttSettings
from zero_prop_test.twincat import Client as TwinCatClient
from zero_prop_test.twincat import Variable as TwinCatVariable
from aiomqtt import Client as MqttClient

type DeviceType = IoLinkDeviceType | int | float | bool | Any
type AddressType = IoLinkDevice | ModbusAddress | TwinCatVariable


class Message(BaseModel):
    timestamp: datetime
    devices: dict[str, DeviceType]


class Loop:
    def __init__(
        self,
        mqtt: MqttClient,
        interval: timedelta,
        iolink_client: IoLinkClient | None = None,
        modbus_client: ModbusClient | None = None,
        twincat_client: TwinCatClient | None = None,
    ):
        self._iolink_client = iolink_client
        self._modbus_client = modbus_client
        self._twincat_client = twincat_client
        self._mqtt = mqtt
        self._interval = interval

    @staticmethod
    @asynccontextmanager
    async def from_settings(
        settings: MqttSettings,
        iolink_client: IoLinkClient | None = None,
        modbus_client: ModbusClient | None = None,
        twincat_client: TwinCatClient | None = None,
        interval: timedelta = timedelta(seconds=1),
    ) -> AsyncGenerator["Loop", None]:
        async with MqttClient(
            hostname=settings.mqtt_host,
            port=settings.mqtt_port,
            username=settings.mqtt_username,
            password=settings.mqtt_password,
        ) as mqtt:
            yield Loop(
                mqtt=mqtt,
                interval=interval,
                iolink_client=iolink_client,
                modbus_client=modbus_client,
                twincat_client=twincat_client,
            )

    async def _collect_one(self, address: AddressType) -> DeviceType:
        if isinstance(address, IoLinkDevice):
            if self._iolink_client is None:
                raise ValueError("IO-Link client is not configured")
            return await self._iolink_client.query(address)

        if isinstance(address, ModbusAddress):
            if self._modbus_client is None:
                raise ValueError("Modbus client is not configured")
            return self._modbus_client.query(address.register)

        if isinstance(address, TwinCatVariable):
            if self._twincat_client is None:
                raise ValueError("TwinCAT client is not configured")
            return self._twincat_client.query(address)

        raise TypeError(f"Unsupported address type: {type(address)}")

    async def _collect(self, addresses: Sequence[AddressType]) -> dict[str, DeviceType]:
        return {address.name: await self._collect_one(address) for address in addresses}

    async def tick(self, addresses: Sequence[AddressType]):
        data = await self._collect(addresses)
        message = Message(timestamp=datetime.now(), devices=data)
        await self._mqtt.publish("prop-test/data", message.model_dump_json())

    async def run(self, addresses: Sequence[AddressType]):
        while True:
            async with TaskGroup() as tg:
                tg.create_task(sleep(self._interval.total_seconds()))
                tg.create_task(self.tick(addresses))
