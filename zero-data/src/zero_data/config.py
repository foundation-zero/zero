from typing import Annotated

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from zero_data.io_list.types import Source

io_lists: list[tuple[Source, list[str]]] = [
    (
        "marpower",
        [
            "ZERO mocked IO-List.xlsx",
            "io-list ~ help ~ totals.xlsx",
        ],
    ),
    ("sail_system", ["3094_SailPLC.PLC_MAIN.Application.xml"]),
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
