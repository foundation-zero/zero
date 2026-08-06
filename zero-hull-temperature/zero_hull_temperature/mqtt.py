from typing import Annotated

from pydantic import BaseModel, Field


class MqttValue(BaseModel):
    value: Annotated[bool, Field(alias="Value")]
