from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Annotated

from io_processing.io_list.types import Source


io_lists: list[tuple[Source, str]] = [
    ("marpower", "52422003_3210_AMCS IO-List R2.5.xlsx")
]


class MQTTConfig(BaseSettings):
    host: Annotated[
        str, Field(description="Host name of the MQTT broker", default="localhost")
    ]
    port: Annotated[
        int, Field(description="Port number of the MQTT Broker", default=1883)
    ]

    @property
    def uri(self) -> str:
        return f"{self.host}:{self.port}"

    model_config = SettingsConfigDict(env_prefix="mqtt_")
