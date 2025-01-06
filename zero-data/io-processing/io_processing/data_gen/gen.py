import asyncio
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Any

from aiomqtt import Client
from polars import DataFrame
import polars as pl

from io_processing.generated_components import Description
from io_processing.io_list import (
    DataType,
    IoFlavor,
    data_type_for_value,
    find_type_description,
)
from io_processing.sql.dbt import topic


class Strategy(Enum):
    ZERO = "zero"


@dataclass
class Value:
    topic: str
    type: DataType
    last_value: None | Any = None


class Generator:
    def __init__(
        self, components: DataFrame, description: Description, flavor: IoFlavor
    ) -> None:
        with_signals = components.filter(
            pl.col("signals")
            .list.eval(pl.element().struct.field("value_name").is_not_null())
            .list.all()
        )
        self._values = [
            Value(
                topic(signal["tag"], flavor),
                data_type_for_value(
                    signal["value_name"],
                    find_type_description(
                        component["type"], description.suppliers["marpower"]
                    ),
                ),
            )
            for component in with_signals.iter_rows(named=True)
            for signal in component["signals"]
        ]

    def _next_value(self, value: Value, strategy: Strategy):
        match value.type:
            case DataType.F32:
                return 0.0
            case DataType.I32 | DataType.U32:
                return 0
            case DataType.BOOL:
                return False

    async def _send_value(self, client: Client, value: Value, strategy: Strategy):
        await client.publish(value.topic, str(self._next_value(value, strategy)))

    async def run(self, strategy: Strategy):
        async with Client("vernemq") as client:
            while True:
                async with asyncio.TaskGroup() as tg:
                    for value in self._values:
                        tg.create_task(self._send_value(client, value, strategy))
                await asyncio.sleep(1)
