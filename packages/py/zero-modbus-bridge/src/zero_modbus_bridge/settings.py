from pydantic_settings import BaseSettings, SettingsConfigDict
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer

model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    env_nested_delimiter="__",
    env_prefix="",
    extra="ignore",
)


class ModbusSettings(BaseSettings):
    model_config = model_config

    modbus_host: str
    modbus_port: int
    modbus_probe_interval: int = 10

    def modbus_client(self) -> ModbusClient:
        return ModbusClient(self.modbus_host, self.modbus_port, auto_open=False)

    def modbus_server(self, data_handler=None) -> ModbusServer:
        return ModbusServer(
            self.modbus_host, self.modbus_port, no_block=True, data_hdl=data_handler
        )
