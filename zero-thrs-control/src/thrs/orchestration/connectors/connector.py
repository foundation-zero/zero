from typing import Any, Callable, Protocol


class CommConnector(Protocol):
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
