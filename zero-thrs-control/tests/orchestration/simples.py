from datetime import datetime
from typing import Callable

from thrs.classes.control import Control
from thrs.input_output.alarms import BaseAlarms
from thrs.input_output.base import SimulationInputs, ThrsValues
from thrs.input_output.definitions.sensor import FlowSensor
from thrs.orchestration.connector import Connector
from thrs.orchestration.simulation import Simulation, SimulationResult


class SimpleInOut(ThrsValues):
    go_with_the: FlowSensor


class SimpleSimulationInputs(SimulationInputs):
    pass


class SimpleSimulationOutputs(ThrsValues):
    pass


class SimpleConnector(Connector):
    def __init__(self):
        self.controls = []

    async def run(self):
        pass

    async def transceive(self, control_values):
        self.controls.append(control_values)
        return control_values


class SimpleSimulation(
    Simulation[
        SimpleInOut, SimpleInOut, SimpleSimulationInputs, SimpleSimulationOutputs
    ]
):
    def __init__(self, start_time):
        self.controls = []
        self._start_time = start_time

    async def start(self):
        pass

    def tick(
        self, control_values: SimpleInOut
    ) -> SimulationResult[
        SimpleInOut, SimpleInOut, SimpleSimulationInputs, SimpleSimulationOutputs
    ]:
        self.controls.append(control_values)
        return SimulationResult(
            timestamp=datetime.now(),
            sensor_values=control_values,
            control_values=control_values,
            simulation_outputs=SimpleSimulationOutputs(),
            simulation_inputs=SimpleSimulationInputs(),
            raw={},
        )

    @property
    def start_time(self):
        return self._start_time

    def time(self):
        return datetime.now()


class SimpleParameters(ThrsValues):
    pass


class SimpleMode(ThrsValues):
    pass


class SimpleControl(Control[SimpleInOut, SimpleInOut, SimpleParameters, SimpleMode]):
    def __init__(self, parameters: SimpleParameters, time_fn: Callable[[], datetime]):
        self._parameters = parameters
        self._time = time_fn

    def initial(self) -> SimpleInOut:
        return SimpleInOut.zero()

    def control(self, sensor_values: SimpleInOut) -> SimpleInOut:
        return sensor_values

    @staticmethod
    def modes() -> list[str]:
        return []

    @staticmethod
    def initial_mode() -> str:
        return ""

    @property
    def mode(self) -> SimpleMode | None:
        return None

    @property
    def parameters(self) -> SimpleParameters:
        return SimpleParameters()

    def update_parameters(self, parameters: SimpleParameters):
        pass


class SimpleAlarms(BaseAlarms[SimpleInOut, SimpleInOut, SimpleParameters]):
    pass
