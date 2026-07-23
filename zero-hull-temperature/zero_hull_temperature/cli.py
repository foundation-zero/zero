import asyncio
import json
import logging
from typing import Literal

from faststream import FastStream
from faststream.mqtt import MQTTBroker
from faststream.specification.asyncapi import AsyncAPI
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliMutuallyExclusiveGroup,
    CliSubCommand,
    SettingsConfigDict,
)
from zero_modbus_bridge.bridge import ModbusBridge
from zero_modbus_bridge.publisher import MqttPublisher
from zero_modbus_bridge.settings import ModbusSettings, MqttSettings

from zero_hull_temperature.addresses import HULL_TEMPERATURE_TOPIC, PATH, TOPIC
from zero_hull_temperature.bridge_relay import RelaySwitchingBridge
from zero_hull_temperature.stub import Stub

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


class MqttSend(CliMutuallyExclusiveGroup):
    mqtt: MqttSettings | None = None
    skip_mqtt: Literal[True] | None = None


class ReadWithMqttCmd(ModbusSettings, MqttSettings):
    activate_topic: str = TOPIC
    activate_json_path: str = PATH

    async def cli_cmd(self) -> None:
        async with self.make_broker() as broker:
            MqttPublisher(broker, [HULL_TEMPERATURE_TOPIC])
            bridge = RelaySwitchingBridge.from_settings(
                self,
                broker,
                self.activate_topic,
                self.activate_json_path,
            )
            await bridge.run_once()
        print("Read complete — temperatures published to MQTT")


class ReadSkipMqttCmd(ModbusSettings):
    async def cli_cmd(self) -> None:
        broker = MqttSettings(mqtt_host="localhost", mqtt_port=1883).make_broker()
        async with broker:
            bridge = ModbusBridge.from_settings(self, broker, [HULL_TEMPERATURE_TOPIC])
            await bridge.run_once()
        print("Read complete — temperatures published to MQTT")


class StubCmd(ModbusSettings, MqttSettings):
    temperature: float = 20
    seconds: int = -1

    async def cli_cmd(self) -> None:
        async with Stub.from_settings(
            self, self, TOPIC, PATH, self.temperature
        ) as stub:
            print("Running stub...")
            task = asyncio.create_task(await stub.run())
            if self.seconds == -1:
                await task
            else:
                await asyncio.sleep(self.seconds)
                task.cancel()


class RunCmd(ModbusSettings, MqttSettings):
    activate_topic: str = TOPIC
    activate_json_path: str = PATH

    def cli_cmd(self) -> None:
        import asyncio

        broker = self.make_broker()
        MqttPublisher(broker, [HULL_TEMPERATURE_TOPIC])
        bridge = RelaySwitchingBridge.from_settings(
            self,
            broker,
            self.activate_topic,
            self.activate_json_path,
        )
        app = FastStream(broker)
        app.after_startup(bridge.run)
        asyncio.run(app.run())


class SchemaCmd(BaseModel):
    async def cli_cmd(self) -> None:
        from zero_hull_temperature.addresses import HullTemperature

        print(HullTemperature.model_json_schema())


class AsyncApiCmd(BaseSettings):
    title: str = "Hull Temperature"
    version: str = "1.0.0"

    def cli_cmd(self) -> None:
        broker = MQTTBroker("localhost:1883")
        spec = AsyncAPI(title=self.title, version=self.version)
        app = FastStream(broker, specification=spec)
        MqttPublisher(broker, [HULL_TEMPERATURE_TOPIC])
        print(json.dumps(app.schema.to_specification().to_jsonable(), indent=2))


class ZeroHullTemperature(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        cli_implicit_flags=True,
        cli_ignore_unknown_args=True,
    )

    read_with_mqtt: CliSubCommand[ReadWithMqttCmd]
    read_skip_mqtt: CliSubCommand[ReadSkipMqttCmd]
    stub: CliSubCommand[StubCmd]
    run: CliSubCommand[RunCmd]
    print_schema: CliSubCommand[SchemaCmd]
    print_asyncapi: CliSubCommand[AsyncApiCmd]

    def cli_cmd(self) -> None:
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
