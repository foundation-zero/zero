from datetime import datetime
from thrs.orchestration.collector import NullCollector
from thrs.orchestration.cycler import Cycler
from tests.orchestration.simples import (
    SimpleAlarms,
    SimpleControl,
    SimpleExecutor,
    SimpleParameters,
)


async def test_interfacer():
    control = SimpleControl(SimpleParameters(), lambda: datetime.now())
    executor = SimpleExecutor(datetime.now())
    interfacer = Cycler(control, executor, SimpleAlarms())
    await interfacer.run(3, NullCollector())
    assert len(executor.controls) == 3
    assert executor.controls[0].go_with_the.flow.value == 0
    assert executor.controls[0].go_with_the.temperature.value == 0
