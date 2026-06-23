

import logging

from aiomqtt import Client

from thrs.input_output.base import CombinedValues, ThrsValues
from thrs.orchestration.connectors.connector import Connector
from thrs.orchestration.connectors.mqtt.mapping import (
    DirectMqttMapping,
    ModuleMqttMapping,
    MqttMapping,
)
from thrs.orchestration.module import ModuleClassMap
from thrs.orchestration.simulation import Simulation, SimulationResult

logger = logging.getLogger(__name__)
# niet gebruiken, hooguit wat overnemen
class MqttSimulationConnector(Connector[CombinedValues, CombinedValues]):
    def __init__(
        self,
        simulation: "Simulation",
        mqtt_client: Client,
        topic_prefix: str,
        sensor_values_clss: ModuleClassMap,
        simulation_outputs_cls: type[ThrsValues],
    ):
        self._simulation = simulation
        self._mqtt_client = mqtt_client
        self._topic_prefix = topic_prefix
        self._sensor_values_mqtt_mapping = ModuleMqttMapping(
            sensor_values_clss, topic_prefix
        )
        self._simulation_outputs_mqtt_mapping = DirectMqttMapping(
            simulation_outputs_cls, f"{topic_prefix}/simulation/outputs"
        )

    async def _publish_by_mapping[T](
        self, client: Client, mapping: MqttMapping[T], value: T
    ):
        payloads = mapping.split_to_topics(value)
        for topic, payload in payloads.items():
            await client.publish(topic, payload, qos=1)

    async def _send_sensor_values(self, execution_result: SimulationResult):
        logger.debug("Publishing sensor values")
        await self._publish_by_mapping(
            self._mqtt_client,
            self._sensor_values_mqtt_mapping,
            execution_result.sensor_values,
        )

    async def _send_simulation_output(self, simulation_result: SimulationResult):
        logger.debug("Publishing simulation output values")
        await self._publish_by_mapping(
            self._mqtt_client,
            self._simulation_outputs_mqtt_mapping,
            simulation_result.simulation_outputs,
        )

    async def run(self):
        pass

    async def transceive(self, control_values: CombinedValues) -> CombinedValues:
        logger.debug("Executing simulation")
        simulation_result = self._simulation.tick(control_values)

        logger.debug("Simulation tick completed")
        await self._send_sensor_values(simulation_result)
        await self._send_simulation_output(simulation_result)

        return simulation_result.sensor_values
