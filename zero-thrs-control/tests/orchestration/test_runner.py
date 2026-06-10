from datetime import datetime

from tests.orchestration.simples import (
    SimpleAlarms,
    SimpleControl,
    SimpleExecutor,
    SimpleParameters,
)
from thrs.orchestration.runner import Runner


async def test_simulator():
    control = SimpleControl(SimpleParameters(), lambda: datetime.now())
    executor = SimpleExecutor(datetime.now())
    runner = Runner(executor, control, SimpleAlarms())
    await runner.run(3)
    assert len(executor.controls) == 3
    assert executor.controls[0].go_with_the.flow.value == 0
    assert executor.controls[0].go_with_the.temperature.value == 0
