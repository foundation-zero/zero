from datetime import datetime

from tests.orchestration.simples import (
    SimpleAlarms,
    SimpleConnector,
    SimpleControl,
    SimpleParameters,
    SimpleSimulation,
    SimpleSimulationOutputs,
)
from thrs.orchestration.runner import Runner


async def test_simulator():
    simulation = SimpleSimulation(datetime.now())
    control = SimpleControl(SimpleParameters(), simulation.time)
    connector = SimpleConnector()
    simulation_connector = SimpleConnector()
    runner = Runner(
        connector, "simple", simulation, simulation_connector, control, SimpleAlarms()
    )  # type: ignore
    await runner.run(3)
    assert len(connector.controls) == 3
    assert connector.controls[0][0].go_with_the.flow.value == 0
    assert connector.controls[0][0].go_with_the.temperature.value == 0
    assert len(simulation_connector.controls) == 3
    assert simulation_connector.controls[0][0].go_with_the.flow.value == 0
    assert simulation_connector.controls[0][0].go_with_the.temperature.value == 0
    assert isinstance(
        simulation_connector.controls[0][1].values["simple"], SimpleSimulationOutputs
    )
