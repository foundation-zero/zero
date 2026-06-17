import logging
from typing import Any, Callable, Dict, Protocol

from thrs.orchestration.connectors.connector import CommConnector
from thrs.orchestration.simulation_directives import SimulationCtrlMessage


class Runnable(Protocol):
    paused: bool = False
    tick_rate: float = 1.0
    name: str
    topic_base: str
    comm_connector: CommConnector

    _parameters: Dict[str, Any]

    logger: logging.Logger
    on_directive_received: Callable[[SimulationCtrlMessage], None] | None

    def tick(self) -> None: ...

    def get_status(self) -> str:
        return "OK"

    def update_parameters(self, parameters: Dict[str, Any]):
        self._parameters = parameters

    def __init__(self, name: str, topic_base: str, comm_connector: CommConnector):
        self.name = name
        self.topic_base = topic_base
        self.comm_connector = comm_connector

        self.on_directive_received = None

        self.logger = logging.getLogger(__name__)

        self.logger.debug(
            f"Initialized Runnable: '{self.name}' with topic base: {self.topic_base}"
        )

    def _on_directive_received(self, directive: SimulationCtrlMessage):
        self.logger.debug(f"Received directive for '{self.name}': {directive}")

        # TODO Should parse directives and set locals
        self.tick_rate = 1.0
        self.paused = False
        if self.on_directive_received:
            self.on_directive_received(directive)
