from datetime import datetime

from tests.orchestration.simples import (
    SimpleAlarms,
    SimpleConnector,
    SimpleControl,
    SimpleParameters,
)
from thrs.orchestration.runner import Runner


async def test_simulator():
    control = SimpleControl(SimpleParameters(), lambda: datetime.now())
    connector = SimpleConnector()
    simulation_connector = SimpleConnector()
    runner = Runner(connector, simulation_connector, control, SimpleAlarms())  # type: ignore
    await runner.run(3)
    assert len(connector.controls) == 3
    assert connector.controls[0].go_with_the.flow.value == 0
    assert connector.controls[0].go_with_the.temperature.value == 0
    assert len(simulation_connector.controls) == 3
    assert simulation_connector.controls[0].go_with_the.flow.value == 0
    assert simulation_connector.controls[0].go_with_the.temperature.value == 0
