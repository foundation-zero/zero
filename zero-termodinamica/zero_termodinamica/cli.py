import asyncio
import logging
from datetime import timedelta

from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
    SettingsConfigDict,
)

from zero_termodinamica.reader import ModbusToMQTTBridge
from zero_termodinamica.settings import ModbusSettings, MqttSettings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


class RunCmd(ModbusSettings, MqttSettings):
    send_topic: str
    seconds: int
    n: int = -1

    async def cli_cmd(self) -> None:
        async with ModbusToMQTTBridge.from_settings(self, self) as reader:
            await reader.run()


class ZeroTermodinamica(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )
    run: CliSubCommand[RunCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)
