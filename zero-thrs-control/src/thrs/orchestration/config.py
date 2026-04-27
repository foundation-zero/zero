from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )
    mqtt_host: str
    mqtt_port: int
    mqtt_topic_prefix: str
    mqtt_control_topic_suffix: str
    thrs_environment: Literal["boat", "simulation"] = "simulation"
