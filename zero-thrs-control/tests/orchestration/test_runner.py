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
    connector = SimpleConnector(datetime.now())
    runner = Runner(connector, control, SimpleAlarms())
    await runner.run(3)
    assert len(connector.controls) == 3
    assert connector.controls[0].go_with_the.flow.value == 0
    assert connector.controls[0].go_with_the.temperature.value == 0
