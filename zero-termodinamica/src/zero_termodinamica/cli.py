import logging

from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliSubCommand,
)

from zero_termodinamica.io import read_modbus_units
from zero_termodinamica.modbus_rtu_to_mqtt import ModbusRtuToMqttBridge
from zero_termodinamica.modbus_to_mqtt import ModbusToMQTTBridge
from zero_termodinamica.settings import (
    ModbusSerialSettings,
    ModbusSettings,
    MqttSettings,
)
from zero_termodinamica.stub import Stub

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


class RunCmd(ModbusSettings, MqttSettings):
    async def cli_cmd(self) -> None:
        async with ModbusToMQTTBridge.from_settings(
            self, self, read_modbus_units()
        ) as reader:
            await reader.run()


class StubCmd(ModbusSettings):
    default_value: int = 20

    def cli_cmd(self) -> None:
        stub = Stub.from_settings(self, read_modbus_units(), self.default_value)
        stub.run()


class RunRTUCmd(ModbusSerialSettings, MqttSettings):
    async def cli_cmd(self) -> None:
        async with ModbusRtuToMqttBridge.from_settings(
            self, self, read_modbus_units()
        ) as reader:
            await reader.run()


class ZeroTermodinamica(BaseSettings, cli_kebab_case=True):
    run: CliSubCommand[RunCmd]
    stub: CliSubCommand[StubCmd]
    run_rtu: CliSubCommand[RunRTUCmd]

    def cli_cmd(self) -> None:
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
