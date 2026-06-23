import asyncio
import contextlib
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Literal,
    Protocol,
    overload,
)

from src.thrs.input_output.base import CombinedValues, ThrsValues
from thrs.cli.config.modes import CommConnectorMode
from thrs.orchestration.config import Config

if TYPE_CHECKING:
    from thrs.orchestration.connectors.memory_connector import MemoryConnector
    from thrs.orchestration.connectors.mqtt_connector import MqttConnector


class CommConnector[S, C](Protocol):
    async def run(self): ...

    @overload
    @classmethod
    @contextlib.asynccontextmanager  # <-- Add this decorator!
    async def create(
        settings: Config, mode: Literal[CommConnectorMode.MQTT]
    ) -> "MqttConnector": ...
    @overload
    @classmethod
    @contextlib.asynccontextmanager  # <-- Add this decorator!
    async def create(
        settings: Config, mode: Literal[CommConnectorMode.MEMORY]
    ) -> "MemoryConnector": ...

    @classmethod
    @contextlib.asynccontextmanager  # <-- Add this decorator!
    async def create(
        cls, settings: Config, mode: CommConnectorMode = CommConnectorMode.MQTT
    ) -> AsyncGenerator["CommConnector", None]:
        from thrs.orchestration.connectors.mqtt_connector import (
            MqttConnector,  # TODO Maapater: circular import, should be able to import at top level without issues
        )
        
        if mode == CommConnectorMode.MEMORY:
            connector = MemoryConnector()
        else:
            connector = MqttConnector(mqtt_host=settings.mqtt_host)
        task = asyncio.create_task(connector.run())
        await connector.connection_open_event.wait() # Wait for the connection to be established before yielding the connector

        try:
            yield connector
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    def read_values(self, values: ThrsValues) -> CombinedValues | None: ...

    async def send_values(self, values: ThrsValues): ...
    async def subscribe(self, values: ThrsValues, topic_prefix: str, qos: int = 0): ...

    async def run(self): ...


# TODO Maapater Remove this, but now used as reference
class CommConnectorDepricatedMaaarten(Protocol):
    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...

    def subscribe_to_topic(
        self, topic: str, callback: Callable | None = None
    ) -> None: ...

    def publish_parameters(self, parameters: dict[str, Any]):
        self.publish("parameters", parameters)

    def get_parameters(self) -> dict[str, Any]: ...

    def publish_sensor_values(self, sensor_values: dict[str, Any]):
        self.publish("sensor_values", sensor_values)

    def get_sensor_values(self) -> dict[str, Any]: ...

    def publish_command_values(self, command_values: dict[str, Any]) -> None:
        self.publish("command_values", command_values)

    def get_command_values(self) -> dict[str, Any]: ...

    def publish(self, topic: str, payload: dict[str, Any]) -> None: ...
