import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from time import time
from typing import Any

from src.thrs.cli.simulation_controls import DIRECTIVES
from src.thrs.orchestration.connectors.mqtt.mapping import (
    DirectMqttMapping,
    ModuleMqttMapping,
    PartialMqttMapping,
)
from thrs.cli.runner.runnables.runnable import Runnable
from thrs.input_output.base import SimulationInputs, SimulationValues, ThrsValues
from thrs.orchestration.connectors.base import CommConnector
from thrs.orchestration.connectors.data_definitions import (
    SimulationModuleDefinition,
)
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import CombinedIoMapping, IoMapping, ThrsModelIoMapping

logger = logging.getLogger(__name__)


@dataclass
class SimulationResult[
    S,
    C,
    I: SimulationInputs,
    O: SimulationValues,
]:
    timestamp: datetime
    sensor_values: S
    control_values: C
    simulation_outputs: O
    simulation_inputs: I
    raw: dict[str, Any]


class SimulationRunnable(Runnable):
    def __init__(
        self,
        comm_connector: CommConnector,
        simulation_model_definition: SimulationModuleDefinition,
        fmu: Fmu,
        start_time: datetime,
        tick_duration: timedelta,
    ):
        self._start_time = start_time
        self._ticks = 0
        self._tick_duration = tick_duration
        self._time_spent = start_time
        self.simulation_inputs: type[ThrsValues] = simulation_model_definition.input_values  # TODO Maapater Correct?
        self.simulation_outputs: type[ThrsValues] = simulation_model_definition.output_values_type  # TODO Maapater Correct?
        self._fmu_inputs = []
        self._fmu = fmu

        # TODO Maapater: Start Mqtt issue
        # TODO Maapater: (1) input/output/parameters convert to MqttMapping, (2) use mqtt mapping to subscribe to topics and send values
        self.input_topic = f"{simulation_model_definition.topic_base}/input"  # TODO Maapater: This is wrong
        self.output_topic = f"{simulation_model_definition.topic_base}/output"  # TODO Maapater: This is wrong
        self.sensor_topic = f"{simulation_model_definition.topic_base}/sensor"  # TODO Maapater: This is wrong

        self.input_mqtt_mapping = PartialMqttMapping(cls=
            simulation_model_definition.input_values,  topic_prefix=self.input_topic,module_prefix="?"
        )
        self.output_mqtt_mapping = PartialMqttMapping(
            cls=simulation_model_definition.output_values_type, topic_prefix=self.output_topic,module_prefix="?"
        )
        self.sensor_mqtt_mapping = PartialMqttMapping(
            cls=simulation_model_definition.sensor_values_type, topic_prefix=self.sensor_topic,module_prefix="?"
        )

        # TODO: maapater: IO Mapping nog nodig?
        self._io_mapping: IoMapping = (
            CombinedIoMapping(
                simulation_model_definition.sensor_values_type,
                simulation_model_definition.output_values_type,
            )
            if isinstance(simulation_model_definition.sensor_values_type, dict)
            else ThrsModelIoMapping(
                simulation_model_definition.sensor_values_type,
                simulation_model_definition.output_values_type,
            )  # type: ignore
        )

        self.comm_connector = comm_connector
        self.sensor_values: type[ThrsValues] = simulation_model_definition.sensor_values_type

    def update_input(self):
        logging.debug("Receive sensor values")
        self.comm_connector.read_values(self.sensor_values)

    def tick(self):
        logging.debug("Running simulation tick")
        time = self.time()

        # Construct FMU input
        sim_input = self.simulation_inputs.get_values_at_time(time)
        fmu_inputs = self._io_mapping.generate_inputs(self.sensor_values, sim_input)

        # Tick simulation
        fmu_outputs = self._fmu.tick(fmu_inputs, self._tick_duration)

        # Get outputs
        sensor_values, simulation_outputs, raw = self._io_mapping.construct_outputs(
            fmu_inputs, fmu_outputs, sim_input, time + self._tick_duration
        )

        # TODO Maapater: Send outputs to MQTT topics
        self.comm_connector.send_values(simulation_outputs)

        self._ticks += 1
        self._time_spent += self._tick_duration

        # control_values = self._sensor_values

        # return SimulationResult(
        #     timestamp=time,
        #     sensor_values=sensor_values,
        #     control_values=control_values,
        #     simulation_outputs=simulation_outputs,
        #     simulation_inputs=sim_input,
        #     raw=raw,
        # )

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def tick_duration(self) -> timedelta:
        return self._tick_duration

    def time(self):
        return self._time_spent

    def update_simulation_inputs(self, simulation_inputs: SimulationInputs):
        self.simulation_inputs = simulation_inputs

    @classmethod
    async def create(
        cls,
        comm_connector: CommConnector,
        simulation_definition: SimulationModuleDefinition,
        minimal_time_between_tick_iterations: float,
    ) -> "SimulationRunnable":
        fmu: Fmu = Fmu(simulation_definition.fmu_path)

        simulation: SimulationRunnable = SimulationRunnable(
            comm_connector,
            simulation_definition,
            fmu,
            time(),
            minimal_time_between_tick_iterations,
        )

        # TODO Maapater: (1) input/output/parameters convert to MqttMapping, (2) use mqtt mapping to subscribe to topics and send values
        await simulation.subscribe_to_topics(
            simulation.simulation_inputs, simulation.input_topic
        )
        await simulation.subscribe_to_topics(
            simulation.simulation_outputs, simulation.output_topic
        )
        await simulation.subscribe_to_topics(
            simulation.sensor_values,
            simulation.sensor_topic,
        )
        await simulation.subscribe_to_topics(items=DIRECTIVES, topic="", qos=1)

        return simulation
