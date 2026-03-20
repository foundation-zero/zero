from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    iolink_host: str
    iolink_port: int
    modbus_host: str
    modbus_port: int
    twincat_self_netid: str
    twincat_ip: str
    twincat_netid: str
    twincat_username: str
    twincat_password: str
    twincat_route_name: str
    mqtt_host: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
