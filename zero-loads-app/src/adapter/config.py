from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )
    mqtt_host: str
    mqtt_port: int

    canbus_ip: str
    canbus_port: int
    canbus_buffer_size: int

    jwt_secret: str
