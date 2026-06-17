from typing import Any, Callable

from thrs.orchestration.connectors.connector import CommConnector


class MqttConnector(CommConnector):
    def __init__(self, mqtt_broker: str):
        self._mqtt_broker = mqtt_broker

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    def subscribe_to_topic(
        self, topic: str, callback: Callable[..., Any] | None = None
    ) -> None:
        raise NotImplementedError

    def get_parameters(self) -> dict[str, Any]:
        raise NotImplementedError

    def get_sensor_values(self) -> dict[str, Any]:
        raise NotImplementedError

    def get_command_values(self) -> dict[str, Any]:
        raise NotImplementedError

    def publish(self, topic: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError
