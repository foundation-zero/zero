from pydantic_settings import BaseSettings, SettingsConfigDict

_env_config = SettingsConfigDict(
    env_file=".env", env_file_encoding="utf-8", extra="ignore"
)


class MqttSettings(BaseSettings):
    model_config = _env_config

    mqtt_host: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str


class IoLinkSettings(BaseSettings):
    model_config = _env_config

    iolink_host: str
    iolink_port: int


class ModbusSettings(BaseSettings):
    model_config = _env_config

    modbus_host: str
    modbus_port: int


class TwinCatSettings(BaseSettings):
    model_config = _env_config

    twincat_self_netid: str
    twincat_ip: str
    twincat_netid: str
    twincat_username: str
    twincat_password: str
    twincat_route_name: str


class Settings(MqttSettings, IoLinkSettings, ModbusSettings, TwinCatSettings):
    model_config = _env_config


class TwinCatOnlySettings(MqttSettings, TwinCatSettings):
    model_config = _env_config
