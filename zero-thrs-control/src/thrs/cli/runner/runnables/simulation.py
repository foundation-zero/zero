from thrs.cli.runner.runner import Runnable, SimulationMode
from thrs.orchestration.connectors.connector import CommConnector


class SimulationRunnable(Runnable):
    def __init__(
        self,
        simulation_mode: SimulationMode,
        topic_base: str,
        comm_connector: CommConnector,
    ):
        name = f"simulation_{simulation_mode.value}"

        super().__init__(name, topic_base, comm_connector)

        self.subscribe_to_sensor_topics()
        self.subscribe_to_parameter_topics()

        self.init_fmu()

    def init_fmu(self):
        self.fmu = None

    def get_tick_rate(self) -> float:
        return 1.0

    def tick(self):
        # Placeholder for simulation tick logic

        current_parameters = self.comm_connector.get_parameters()
        current_commands = self.comm_connector.get_command_values()

        # sensor_values = self.fmu.tick(current_parameters, current_commands)
        sensor_values = {}

        self.comm_connector.publish_sensor_values(sensor_values)

    def subscribe_to_parameter_topics(self):
        self.comm_connector.subscribe_to_topic(f"{self.topic_base}/parameters")

    def subscribe_to_sensor_topics(self):
        self.comm_connector.subscribe_to_topic(f"{self.topic_base}/sensor")
