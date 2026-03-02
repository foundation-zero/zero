from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from typing import Annotated, List, Tuple

from zero_data.io_list.types import Source


io_lists: List[Tuple[Source, List[str]]] = [
    (
        "marpower",
        [
            "ZERO mocked IO-List.xlsx",
            "52422003_3210_AMCS IO-List R2.29.xlsx",
            "52422003_3211_PMS IO-List R2.12-fixed2.xlsx",
        ],
    )
]


class MQTTConfig(BaseSettings):
    host: Annotated[
        str, Field(description="Host name of the MQTT broker", default="localhost")
    ]
    port: Annotated[
        int, Field(description="Port number of the MQTT Broker", default=1883)
    ]

    @computed_field  # type: ignore[misc]
    @property
    def uri(self) -> str:
        return f"{self.host}:{self.port}"

    model_config = SettingsConfigDict(env_prefix="mqtt_")
