import asyncio
from datetime import timedelta
import json
import logging
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliMutuallyExclusiveGroup,
    CliSubCommand,
    SettingsConfigDict,
)

from zero_hull_temperature.addresses import PATH, TOPIC
from zero_hull_temperature.mqtt import Temperatures
from zero_hull_temperature.settings import ModbusSettings, MqttSettings
from zero_hull_temperature.stub import Stub
from zero_hull_temperature.reader import (
    RelaySwitchingTemperatureReader,
    TemperatureReader,
)

logging.basicConfig(level=logging.INFO)


class MqttSend(CliMutuallyExclusiveGroup):
    mqtt: MqttSettings | None = None
    skip_mqtt: Literal[True] | None = None


class ReadWithMqttCmd(ModbusSettings, MqttSettings):
    activate_topic: str = TOPIC
    activate_json_path: str = PATH

    async def cli_cmd(self) -> None:
        async with RelaySwitchingTemperatureReader.from_settings(
            self, self, self.activate_topic, self.activate_json_path, ""
        ) as reader:
            temperatures = await reader.read_temperatures()
            print(Temperatures(temperatures=temperatures).model_dump_json(indent=2))


class ReadSkipMqttCmd(ModbusSettings):
    async def cli_cmd(self) -> None:
        async with TemperatureReader.from_settings(self) as reader:
            temperatures = await reader.read_temperatures()
            print(Temperatures(temperatures=temperatures).model_dump_json(indent=2))


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
    send_topic: str
    seconds: int
    n: int = -1

    async def cli_cmd(self) -> None:
        async with RelaySwitchingTemperatureReader.from_settings(
            self, self, self.activate_topic, self.activate_json_path, self.send_topic
        ) as reader:
            await reader.run(timedelta(seconds=self.seconds), n=self.n)


class SchemaCmd(BaseModel):
    async def cli_cmd(self) -> None:
        print(json.dumps(Temperatures.model_json_schema(), indent=2))


class ZeroHullTemperature(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )
    read: CliSubCommand[ReadWithMqttCmd]
    read_skip_mqtt: CliSubCommand[ReadSkipMqttCmd]
    stub: CliSubCommand[StubCmd]
    run: CliSubCommand[RunCmd]
    print_schema: CliSubCommand[SchemaCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
