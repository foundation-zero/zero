import json
import logging

from faststream import FastStream
from faststream.mqtt import MQTTBroker
from faststream.specification.asyncapi import AsyncAPI
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
)
from zero_modbus_bridge.bridge import ModbusBridge
from zero_modbus_bridge.publisher import MqttPublisher
from zero_modbus_bridge.settings import ModbusSettings, MqttSettings
from zero_modbus_bridge.stub import Stub

from zero_termodinamica.io import read_modbus_topics

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


class RunCmd(ModbusSettings, MqttSettings):
    async def cli_cmd(self) -> None:
        broker = self.make_broker()
        topics = read_modbus_topics()
        bridge = ModbusBridge.from_settings(self, broker, topics)
        app = FastStream(broker)
        app.after_startup(bridge.run)
        await app.run()


class StubCmd(ModbusSettings):
    default_value: int = 20

    def cli_cmd(self) -> None:
        stub = Stub.from_settings(self, read_modbus_topics(), self.default_value)
        stub.run()


class AsyncApiCmd(BaseSettings):
    title: str = "Termodinamica"
    version: str = "1.0.0"

    def cli_cmd(self) -> None:
        broker = MQTTBroker("localhost:1883")
        spec = AsyncAPI(title=self.title, version=self.version)
        app = FastStream(broker, specification=spec)
        MqttPublisher.register_publishers(broker, read_modbus_topics())
        print(json.dumps(app.schema.to_specification().to_jsonable(), indent=2))


class ZeroTermodinamica(BaseSettings, cli_kebab_case=True):
    run: CliSubCommand[RunCmd]
    stub: CliSubCommand[StubCmd]
    print_asyncapi: CliSubCommand[AsyncApiCmd]

    def cli_cmd(self) -> None:
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
