import asyncio
import logging
from datetime import timedelta

from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from zero_termodinamica.modbus_to_mqtt import ModbusToMQTTBridge
from zero_termodinamica.settings import ModbusSettings, MqttSettings
from zero_termodinamica.stub import Stub

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


class BaseCommandSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="",
        extra="ignore",
    )


class RunCmd(BaseCommandSettings, ModbusSettings, MqttSettings):
    async def cli_cmd(self) -> None:
        async with ModbusToMQTTBridge.from_settings(self, self) as reader:
            await reader.run()


class StubCmd(BaseCommandSettings, ModbusSettings, MqttSettings):
    default_value: int = 20

    def cli_cmd(self) -> None:
        stub = Stub.from_settings(self, self.default_value)
        stub.run()


class ZeroTermodinamica(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="",
        extra="ignore",
    )
    run: CliSubCommand[RunCmd]
    stub: CliSubCommand[StubCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
