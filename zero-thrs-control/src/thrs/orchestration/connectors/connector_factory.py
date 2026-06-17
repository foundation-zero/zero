from typing import Literal, overload

from thrs.cli.config.modes import CommConnectorMode
from thrs.orchestration.config import Config
from thrs.orchestration.connectors.connector import CommConnector
from thrs.orchestration.connectors.memory_connector import MemoryConnector
from thrs.orchestration.connectors.mqtt_connector import MqttConnector


@overload
def get_connector(
    settings: Config, mode: Literal[CommConnectorMode.MQTT]
) -> MqttConnector: ...
@overload
def get_connector(
    settings: Config, mode: Literal[CommConnectorMode.MEMORY]
) -> MemoryConnector: ...


def get_connector(
    settings: Config, mode: CommConnectorMode = CommConnectorMode.MQTT
) -> CommConnector:
    if mode == CommConnectorMode.MEMORY:
        return MemoryConnector()

    return MqttConnector(mqtt_broker=settings.mqtt_host)
