from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class MQTTConfig(BaseSettings):
    host: str = Field("localhost")
    port: int = Field(1883)

    model_config = SettingsConfigDict(env_prefix="mqtt_")
