from datetime import datetime
from orchestration.collector import NullCollector
from orchestration.interfacer import Interfacer
from tests.orchestration.simples import SimpleControl, SimpleExecutor


async def test_interfacer():
    control = SimpleControl()
    executor = SimpleExecutor(datetime.now())
    interfacer = Interfacer(control, executor)
    await interfacer.run(3, NullCollector())
    assert len(executor.controls) == 3
    assert executor.controls[0].go_with_the.flow.value == 0
    assert executor.controls[0].go_with_the.temperature.value == 0

