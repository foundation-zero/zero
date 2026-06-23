import asyncio
import warnings
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from src.thrs.cli.runner.messaging import (
    DIRECTIVES,
    ControlModeMessage,
)
from src.thrs.cli.runner.runnables.runnable import Runnable
from src.thrs.input_output.base import CombinedValues, ThrsValues
from src.thrs.orchestration import module
from src.thrs.orchestration.connectors.mqtt.mapping import PartialMqttMapping
from src.thrs.orchestration.mqtt import MessageContext
from thrs.classes.control import Control
from thrs.orchestration.connectors.base import CommConnector

if TYPE_CHECKING:
    from thrs.orchestration.connectors.data_definitions import (
        ControlModuleDefinition,
    )


class ControlRunnable(Runnable):
    def __init__(
        self,
        module_definition: "ControlModuleDefinition",
        name: str,
        topic_base: str,
        comm_connector: CommConnector,
        minimal_time_between_tick_iterations: float,
    ):
        super().__init__(name, topic_base, comm_connector)

        self._module_definition: "ControlModuleDefinition" = module_definition
        self._minimal_time_between_tick_iterations = minimal_time_between_tick_iterations
        self.control_input_type: type[ThrsValues] = (
            module_definition.module_description.input_values_type
        )  # Sensor values
        self.control_output_type: type[ThrsValues] = (
            module_definition.module_description.output_values_type
        )  # Control values
        self.control_parameters_type: type[ThrsValues] = (
            module_definition.module_description.parameters_type
        )  # Control parameters

        # TODO Maapater: Start Mqtt issue
        # TODO Maapater: (1) input/output/parameters convert to MqttMapping, (2) use mqtt mapping to subscribe to topics and send values
        self.control_input_topic = module_definition.topic_base # TODO Maapater: This is wrong, use other topic?
        self.control_output_topic = module_definition.topic_base # TODO Maapater: This is wrong, use other topic?
        self.control_parameters_topic = module_definition.topic_base # TODO Maapater: This is wrong, use other topic?


        self.control_input_type = PartialMqttMapping(cls=
            module_definition.module_description.input_values_type,  topic_prefix=self.control_input_topic,module_prefix="?"
        )
        self.control_output_type = PartialMqttMapping(
            cls=module_definition.module_description.output_values_type, topic_prefix=self.control_output_topic,module_prefix="?"
        )
        self.control_parameters_type = PartialMqttMapping(
            cls=module_definition.module_description.parameters_type, topic_prefix=self.control_parameters_topic,module_prefix="?"
        )


        self.init_control()
        self.init_message_context()

        # TODO Maapater Receive will fill CMDS queue
        # cmds queue should be read by SimRunnable.
        # self._receive_task = create_task(
        #         self._receive_controls(DIRECTIVES, self._message_context, modules)
        #     )

    # TODO Maapater Receive 
    # async def __aexit__(self, *args: Any) -> None:
    #     self._receive_task.cancel()
    #     await asyncio.gather(self._receive_task, return_exceptions=True)

    def init_control(self):
        self._control = Control(
            CombinedValues(self.parameters),
            timedelta(seconds=self._minimal_time_between_tick_iterations),
        )

    def init_message_context(self):
        if not self._control:
            raise ValueError("Control not initialized")

        self._message_context = MessageContext(self.comm_connector, self.topic_base)

    async def send_control_modes(self):
        await self._message_context.send(
            ControlModeMessage(
                module=module,
                mode=self._module_definition.module_description.control.mode,
            )
        )
        await self._message_context.send(
            ControlModeMessage(
                module=module,
                mode=self._module_definition.module_description.control_mode_cls.mode,
            )
        )

    def tick(self):
        current_parameters = self.comm_connector.read_values(self._control.parameters)
        current_sensor_values = self.comm_connector.read_values(self.control_input_type)

        self._command_values = self._control.control(
            current_parameters, current_sensor_values
        )

        self.check_alarms(current_sensor_values, self._command_values)

        self.comm_connector.publish_command_values(self._command_values)

    def check_alarms(self, sensor_values: ThrsValues, command_values: ThrsValues):
        alarms = self._alarms.check(
            sensor_values, command_values, self._control.parameters
        )
        if alarms:
            warnings.warn(f"Alarms detected: {alarms}")  # TODO: properly handle alarms

    @classmethod
    async def create(
        cls,
        comm_connector: CommConnector,
        control_module_definition: "ControlModuleDefinition",
        minimal_time_between_tick_iterations: float,
    ) -> "ControlRunnable":
        control: ControlRunnable = await ControlRunnable(
            module_definition=control_module_definition,
            topic_base=control_module_definition.topic_base,
            comm_connector=comm_connector,
            minimal_time_between_tick_iterations=minimal_time_between_tick_iterations,
        )

        # TODO Maapater: (1) input/output/parameters convert to MqttMapping, (2) use mqtt mapping to subscribe to topics and send values
        # TODO Maapater check if subscribe is successful
        await control.subscribe_to_topics(control.control_input_type, control.control_input_topic)
        await control.subscribe_to_topics(control.control_output_type, control.control_output_topic)
        await control.subscribe_to_topics(control.control_parameters_type, control.control_parameters_topic)
        await control.subscribe_to_topics(DIRECTIVES, qos=1)
        await control.send_control_modes()

        return control
