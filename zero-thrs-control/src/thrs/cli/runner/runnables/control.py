from thrs.cli.runner.runner import Runnable
from thrs.orchestration.connectors.connector import CommConnector
from thrs.orchestration.control import Control


class ControlRunnable(Runnable):
    def __init__(self, name: str, topic_base: str, comm_connector: CommConnector):
        super().__init__(name, topic_base, comm_connector)

        self.subscribe_to_sensor_topics()
        self.subscribe_to_parameter_topics()

        self.init_control()
        self.control = Control()

    def init_control(self):
        # init statemachines
        pass

    def get_tick_rate(self) -> float:
        return 1.0

    def tick(self):
        current_parameters = self.comm_connector.get_parameters()
        current_sensor_values = self.comm_connector.get_sensor_values()

        self._command_values = self.control.control(
            current_parameters, current_sensor_values
        )

        self.check_alarms()

        self.comm_connector.publish_command_values(self._command_values)

    def check_alarms(self): ...

    def subscribe_to_parameter_topics(self):
        self.comm_connector.subscribe_to_topic(f"{self.topic_base}/parameters")

    def subscribe_to_sensor_topics(self):
        self.comm_connector.subscribe_to_topic(f"{self.topic_base}/sensor")
