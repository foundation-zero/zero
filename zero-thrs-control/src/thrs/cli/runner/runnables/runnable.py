import logging
from typing import (
    Any,
    Callable,
    Dict,
)

from src.thrs.orchestration.mqtt import IncomingMessage, MessageContext, MqttContext
from thrs.input_output.base import (
    ThrsValues,
)
from thrs.orchestration.connectors.base import CommConnector
from thrs.orchestration.module import CombinedModule
from thrs.orchestration.simulation_directives import SimulationCtrlMessage


class Runnable:
    paused: bool = False
    tick_rate: float = 1.0
    name: str = ""
    topic_base: str = ""
    comm_connector: CommConnector

    parameters: Dict[str, Any]

    logger: logging.Logger
    on_directive_received: (
        Callable[[SimulationCtrlMessage], None] | None
    )  # Subscribe to act on received directives

    def tick(self) -> None: ...

    def update_parameters(self, parameters: Dict[str, Any]):
        self.parameters = parameters

    def update_input(self): ...

    def __init__(self, comm_connector: CommConnector):
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

    async def _receive_controls(
        self,
        handlers: list[type[IncomingMessage]],
        context: MessageContext,
        modules: CombinedModule,
    ):
        async for message in self.comm_connector.messages:
            for handler in handlers:
                if message.topic.matches(
                    f"{self._topic_prefix}/{handler.subscribe_topic()}"
                ) and isinstance(message.payload, (str, bytes)):
                    self.logger.debug(
                        f"Received message on topic {message.topic}, handling {handler}"
                    )

                    # Receive for which module the message is for, to resolve the correct typing for control values and parameters
                    mqtt_context = MqttContext(
                        topic=message.topic.value.removeprefix(
                            f"{self._topic_prefix}/"
                        ),
                    )

                    # TODO Maapater: Is this correct? Use MqqtMappings?
                    resolved_handler = (
                        handler.resolve(
                            modules.control_values_for_module(mqtt_context.module),
                            modules.parameters_for_module(mqtt_context.module),
                            modules.simulation_inputs_cls,
                            modules.simulation_outputs_cls,
                        )
                        if mqtt_context.module
                        in modules.modules  # return self.topic.split("/")[0]
                        else handler.resolve(
                            ThrsValues,
                            ThrsValues,
                            modules.simulation_inputs_cls,
                            modules.simulation_outputs_cls,
                        )
                    )

                    await resolved_handler.model_validate_json(
                        message.payload,
                        context=MqttContext(
                            topic=message.topic.value.removeprefix(
                                f"{self._topic_prefix}/"
                            ),
                        ),
                    ).handle(context)
                    break

    async def subscribe_to_topics(
        self, items: ThrsValues | list[type[IncomingMessage]], topic: str, qos=0
    ):
        if not isinstance(items, (list, tuple, dict, set)):
            items = (items,)

        for item in items:
            await self.comm_connector.subscribe(item, topic, qos=qos)
